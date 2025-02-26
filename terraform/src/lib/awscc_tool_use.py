import os
import asyncio
import boto3
import logging
import time
import sys
from botocore.exceptions import ClientError
from datetime import datetime
from collections.abc import Callable
from typing import Any, cast, Optional
from enum import StrEnum
from functools import partial
from .tools import BashTool, ComputerTool, EditTool, ToolCollection, ToolResult
from anthropic import Anthropic, AnthropicBedrock, APIResponse
from anthropic.types.tool_use_block import ToolUseBlock
from anthropic.types import (
    TextBlock,
)
from anthropic.types.beta import (
    BetaContentBlock,
    BetaContentBlockParam,
    BetaImageBlockParam,
    BetaMessage,
    BetaMessageParam,
    BetaTextBlockParam,
    BetaToolResultBlockParam,
    BetaTextBlock, 
    BetaToolUseBlock
)
from .helpers import explorer, loggers
from .helpers.loggers import LoggerToolLevel
from .helpers.explorer import FileMarker
from .helpers.prompt import (
    SYSTEM_PROMPT,
    USER_PROMPT_CREATE,
    USER_PROMPT_DELETE,
    USER_PROMPT_UPDATE,
    USER_PROMPT_REVIEW,
    USER_PROMPT_CLEANER,
    USER_PROMPT_SUMMARY
)
from .helpers.s3_helper import download_from_s3_prefix, upload_to_s3_prefix

session = boto3.Session(profile_name=os.environ.get('AWS_PROFILE', None))

logger = loggers.setup_logger(
    name="main-function",
    log_level=logging.INFO # log level for regular logging
    )
tool_logger_level = LoggerToolLevel[os.environ.get('LOG_LEVEL', 'L1')] # log level for Anthropic tool use output

class APIProvider(StrEnum):
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"

PROVIDER_TO_DEFAULT_MODEL_NAME: dict[APIProvider, str] = {
    APIProvider.ANTHROPIC: "claude-3-7-sonnet-20250219",
    APIProvider.BEDROCK: "anthropic.claude-3-7-sonnet-20250219-v1:0"
}

class Sender(StrEnum):
    USER = "user"
    BOT = "assistant"
    TOOL = "tool"

# We dont use computer as a tool, but we initialize this here for future-use
os.environ["DISPLAY_NUM"] = "1"
os.environ["HEIGHT"] = "768"
os.environ["WIDTH"] = "1024"

async def sampling_loop(
    *,
    model: str,
    system_prompt_suffix: str,
    messages: list[BetaMessageParam],
    max_tokens: int = 4096,
    sleep_time: int = 10,
    output_callback: Callable[[BetaContentBlock], None],
    tool_output_callback: Callable[[ToolResult, str], None],
    lambda_context: Optional[Any] = None
    ):
    """
    Agentic sampling loop for the assistant/tool interaction of computer use.
    """
    tool_collection = ToolCollection(
        # ComputerTool(), # disable computer use since we dont need full VNC / desktop
        BashTool(),
        EditTool(),
    )
    system = (
        f"{SYSTEM_PROMPT}{' ' + system_prompt_suffix if system_prompt_suffix else ''}"
    )

    credentials = session.get_credentials()
    client = AnthropicBedrock(
        aws_region=os.environ.get('AWS_REGION', 'us-west-2'),
        aws_access_key=credentials.access_key,
        aws_secret_key=credentials.secret_key,
        aws_session_token=credentials.token if hasattr(credentials, 'token') else None,
        max_retries=10,
    )

    while True:
        try:
            if lambda_context:
                # do nothing, Step Function will take care of it
                logger.debug(f"Remaining lambda time: {lambda_context.get_remaining_time_in_millis()} ms")
            
            # Call the API
            raw_response = client.beta.messages.with_raw_response.create(
            max_tokens=max_tokens,
                messages=messages,
                model=model,
                system=system,
                tools=tool_collection.to_params(),
                betas=["computer-use-2024-10-22"],
            )

            response = raw_response.parse()

            messages.append(
                {
                    "role": "assistant",
                    "content": cast(list[BetaContentBlockParam], response.content),
                }
            )

            tool_result_content: list[BetaToolResultBlockParam] = []
            for content_block in cast(list[BetaContentBlock], response.content):
                output_callback(message=content_block)
                if content_block.type == "tool_use":        
                    result = await tool_collection.run(
                        name=content_block.name,
                        tool_input=cast(dict[str, Any], content_block.input),
                    )
                    tool_result_content.append(
                        _make_api_tool_result(result, content_block.id)
                    )
                    tool_output_callback(tool_output=result, tool_id=content_block.id)

            if not tool_result_content:
                return messages

            messages.append({"content": tool_result_content, "role": "user"})

        except Exception as e:
            logger.error(f"## Loop processing error: {str(e)}")
            time.sleep(sleep_time) # nosemgrep - add time sleep as the most common cause of error is Bedrock throttle, todo: catch proper exception

async def run_prompt(
    logger: logging.Logger,
    user_prompt: str,        
    per_inference_sleep: int = 10,
    logger_level: LoggerToolLevel = LoggerToolLevel.ALL,
    lambda_context: Optional[Any] = None
    ):
    
    messages = []
    session_state_tools = {}

    new_message = user_prompt

    messages.append(
        {
            "role": Sender.USER,
            "content": [TextBlock(type="text", text=new_message)],
        }
    )

    messages = await sampling_loop(
        model=PROVIDER_TO_DEFAULT_MODEL_NAME[
            cast(APIProvider, APIProvider.BEDROCK)
        ],
        system_prompt_suffix="",
        messages=messages,
        sleep_time=per_inference_sleep,
        output_callback=partial(_render_message, sender=Sender.BOT, logger=logger, logger_level=logger_level),
        tool_output_callback=partial(_tool_output_callback, tool_state=session_state_tools, logger=logger, logger_level=logger_level),
        lambda_context=lambda_context,
    )

def _render_message(
    sender: Sender,
    logger: logging.Logger,    
    message: str | BetaTextBlock | BetaToolUseBlock | ToolResult,
    logger_level: LoggerToolLevel = LoggerToolLevel.ALL,
    ):

    logger.info("Sender : {}".format(sender))
    # print("Message: {}\n".format(message))

    is_tool_result = not isinstance(message, str) and (
        isinstance(message, ToolResult)
        or message.__class__.__name__ == "ToolResult"
        or message.__class__.__name__ == "CLIResult"
    )
    if not message or (
        is_tool_result
        and not hasattr(message, "error")
        and not hasattr(message, "output")
    ):
        return

    if isinstance(message, BetaTextBlock) or isinstance(message, TextBlock): # General message
        if logger_level in [LoggerToolLevel.ALL, LoggerToolLevel.L1, LoggerToolLevel.L2, LoggerToolLevel.L3]:
            logger.info("Message: {}\n".format(message))
    elif isinstance(message, BetaToolUseBlock) or isinstance(message, ToolUseBlock): # Tool use
        if logger_level in [LoggerToolLevel.ALL, LoggerToolLevel.L2, LoggerToolLevel.L3]:
            logger.info(f"Tool Use: {message.name}\nInput: {message.input}\n")
    elif is_tool_result: # Tool use output
        if logger_level in [LoggerToolLevel.ALL, LoggerToolLevel.L3]:
            message = cast(ToolResult, message)
            if message.output:
                logger.info("Message: {}\n".format(message))
        if message.error:
            logger.error("Message: {}\n".format(message.error))
        if message.base64_image:
            logger.info("Message: picture included, redacted from print")
    else:
        logger.info("Message: {}\n".format(message))

def _tool_output_callback(
    tool_output: ToolResult, 
    tool_id: str, 
    tool_state: dict[str, ToolResult],
    logger: logging.Logger,
    logger_level: LoggerToolLevel = LoggerToolLevel.ALL,
):
    """Handle a tool output by storing it to state and rendering it."""
    tool_state[tool_id] = tool_output
    _render_message(sender=Sender.TOOL, logger=logger, logger_level=logger_level, message=tool_output,)

def _make_api_tool_result(
    result: ToolResult, 
    tool_use_id: str
    ) -> BetaToolResultBlockParam:
    
    """Convert an agent ToolResult to an API ToolResultBlockParam."""
    tool_result_content: list[BetaTextBlockParam | BetaImageBlockParam] | str = []
    is_error = False
    if result.error:
        is_error = True
        tool_result_content = _maybe_prepend_system_tool_result(result, result.error)
    else:
        if result.output:
            tool_result_content.append(
                {
                    "type": "text",
                    "text": _maybe_prepend_system_tool_result(result, result.output),
                }
            )
        if result.base64_image:
            tool_result_content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": result.base64_image,
                    },
                }
            )
    return {
        "type": "tool_result",
        "content": tool_result_content,
        "tool_use_id": tool_use_id,
        "is_error": is_error,
    }

def _maybe_prepend_system_tool_result(result: ToolResult, result_text: str):
    if result.system:
        result_text = f"<system>{result.system}</system>\n{result_text}"
    return result_text
  
async def process_resource(
    target_resource: str,
    dir_path: str,
    base_prompt: str,
    logger: logging.Logger,
    marker_type: FileMarker, 
    per_resource_sleep: int = 60,
    per_inference_sleep: int = 10,
    per_resource_timeout: int = 300,
    re_run: bool = False,
    logger_level: LoggerToolLevel = LoggerToolLevel.ALL,
    lambda_context: Optional[Any] = None
    ):

    execution_times = []
    start_time = time.perf_counter()  # More precise timer

    resource_name = target_resource
    logger.info(f"##################### START : {resource_name} #############################")
    logger.info(f"Action type: {marker_type}")
    logger.info(f"Working directory: {dir_path}")
    
    # Set Terraform init cache
    # os.environ["TF_PLUGIN_CACHE_DIR"]=os.path.join(os.getcwd(), "cache")       

    logger.info(f"Processing resource: {resource_name}")
    skip = False

    # check for marker file and decide if we should proceed or not
    if explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.SKIP):
        # This marker indicate the resource has failed multiple attempt and should be reviewed manually
        logger.info(f"Marker found: {marker_type} - Skipping resource: {resource_name}, remove this marker manually if required")
        skip = True
    elif explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=marker_type) and not re_run:
        # Check if marker type already existed, which indicate whether we should re-run or not
        logger.info(f"Marker found: {marker_type} - Re-run is : {re_run} - resource already processed: {resource_name}, skipping")
        skip = True
    elif re_run:
        logger.info(f"Re-run is : {re_run}, re-processing resource: {resource_name}")
        # If we going to re-run the CREATE or UPDATE process, delete all previous markers
        if marker_type in [FileMarker.CREATED, FileMarker.UPDATED] :
            for marker in FileMarker:
                explorer.delete_marker(dir_path, marker_type=marker)

    # deterministic check for certain file (it's faster than asking LLM to do it)
    if marker_type == FileMarker.DELETED:
        if not explorer.check_if_dir_contains_statefile(dir_path=dir_path):
            logger.warning(f".tfstate file not found - Resource deletion not required : {resource_name}, skipping")
            skip = True
        elif explorer.check_file_size_with_units(file_path=os.path.join(dir_path, "terraform.tfstate"), max_size=200, unit="B"):
            logger.warning(f".tfstate file is empty - Resource deletion not required : {resource_name}, skipping")
            skip = True
    elif marker_type == FileMarker.REVIEWED:
        if (not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.CREATED) or 
            not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.DELETED) 
            ):
            logger.warning(f"{FileMarker.CREATED} or {FileMarker.DELETED} marker not found, Resource not ready for review : {resource_name}, skipping")
            skip = True
    elif marker_type == FileMarker.CLEANED:
        if (not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.CREATED) or 
            not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.DELETED) or 
            not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.REVIEWED) 
            ):
            logger.warning(f"{FileMarker.CREATED} or {FileMarker.DELETED} or {FileMarker.REVIEWED} marker not found, Resource not ready for review : {resource_name}, skipping")
            skip = True
    elif marker_type == FileMarker.SUMMARY:
        if (not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.CREATED) or 
            not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.DELETED) or 
            not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.REVIEWED) or 
            not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.CLEANED)
            ):
            logger.warning(f"{FileMarker.CREATED} or {FileMarker.DELETED} or {FileMarker.REVIEWED} or {FileMarker.CLEANED} marker not found, Resource not ready for review : {resource_name}, skipping")
            skip = True
    
    if skip:
        end_time = time.perf_counter()
        execution_times.append({
            'resource': resource_name,
            'time': end_time - start_time,
            'status': 'skipped'
        })
        logger.info(f"Processing skipped: {resource_name} ({end_time - start_time:.2f} seconds)")
    else:
        user_prompt = base_prompt.format(
            resource_name=resource_name,
            working_directory=dir_path,
            current_date=datetime.today().strftime('%Y-%m-%d')
        )

        try:
            # Wait with timeout
            await asyncio.wait_for(
                run_prompt(
                    user_prompt=user_prompt,
                    per_inference_sleep=per_inference_sleep, # wait / sleep per each cycle of inference (to avoid throttle)
                    logger=logger,
                    logger_level=logger_level,
                    lambda_context=lambda_context), 
                timeout=per_resource_timeout) # async process will attempt to run with max timeout

        except asyncio.TimeoutError:
            logger.error(f"Processing timed out for {resource_name}")
            explorer.delete_directory(dir_path=os.path.join(dir_path, ".terraform"), logger=logger)
            
        except Exception as e:
            logger.error(f"Error processing {resource_name}: {str(e)}")
            explorer.delete_directory(dir_path=os.path.join(dir_path, ".terraform"), logger=logger)

        # time.sleep(per_resource_sleep) # additional wait time per resource to avoid throttle from Bedrock

        # clean up the .terraform directory to save disk space
        if explorer.delete_directory(dir_path=os.path.join(dir_path, ".terraform"), logger=logger):
            logger.info("Succesfully deleted the .terraform directory")

        # If processing completes successfully
        end_time = time.perf_counter()
        execution_times.append({
            'resource': resource_name,
            'time': end_time - start_time,
            'status': 'completed'
        })
        logger.info(f"Completed: {resource_name} ({end_time - start_time:.2f} seconds)")

    logger.info(f"##################### END : {resource_name} #############################\n")

    # After the loop, analyze the timing data with status information
    if execution_times:
        # Calculate statistics for completed tasks
        completed_tasks = [item for item in execution_times if item['status'] == 'completed']
        skipped_tasks = [item for item in execution_times if 'skipped' in item['status']]
        error_tasks = [item for item in execution_times if item['status'] == 'error']

        # Optionally, log details about skipped and error tasks
        if skipped_tasks:
            logger.info("Skipped tasks:")
            for task in skipped_tasks:
                logger.info(f"- {task['resource']}: {task['status']} ({task['time']:.2f} seconds)")

        if error_tasks:
            logger.info("Failed tasks:")
            for task in error_tasks:
                logger.info(f"- {task['resource']}: {task['error']} ({task['time']:.2f} seconds)")

        if completed_tasks:
            total_execution_time = sum(item['time'] for item in completed_tasks) 
            avg_completion_time = sum(item['time'] for item in completed_tasks) / len(completed_tasks)
            max_time = max(completed_tasks, key=lambda x: x['time'])
            min_time = min(completed_tasks, key=lambda x: x['time'])
            
            logger.info("Execution Summary:")
            logger.info(f"Task type: {marker_type}")
            logger.info(f"Total processing time: {total_execution_time:.2f} seconds")
            logger.info(f"Average processing time: {avg_completion_time:.2f} seconds")
            logger.info(f"Longest processing: {max_time['resource']} ({max_time['time']:.2f} seconds)")
            logger.info(f"Shortest processing: {min_time['resource']} ({min_time['time']:.2f} seconds)")
        
        logger.info(f"Total tasks: {len(execution_times)}")
        logger.info(f"Completed: {len(completed_tasks)}")
        logger.info(f"Skipped: {len(skipped_tasks)}")
        logger.info(f"Errors: {len(error_tasks)}")

def build_artifact(
        source_bucket_name: str,
        target_bucket_name: str,
        target_resources: list,
        logger: logging.Logger,
        source_bucket_prefix: Optional[str] = None,
        target_bucket_prefix: Optional[str] = None,
        re_run: bool = False
    ):
    # Lambda always use /tmp for temporary files
    source_local_dir = "/tmp/target_resources"
    target_local_dir = "/tmp/output"
    explorer.create_directory(base_path="/tmp", directory_name="output",logger=logger)

    # payload may contain non string item if the upstream processing failed
    target_resources = [item for item in target_resources if isinstance(item, str)]

    # Download from the source (per resources)
    source_download_result = download_from_s3_prefix(
        bucket_name=source_bucket_name,
        prefix=source_bucket_prefix,
        local_directory=source_local_dir,
        include_prefixes=target_resources,
        exclude_prefixes=[".terraform"],
        logger=logger
    )

    # Initialize counters at the start
    successful_count = 0
    skipped_count = 0
    failed_count = 0
    total_count = len(target_resources)

    for resource_name in sorted(target_resources):
        short_resource_name = resource_name.split("awscc_")[1]
        dir_path = f"{source_local_dir}/{resource_name}"

        logger.info(f"##################### START : {resource_name} #############################")
        logger.info(f"Action type: {FileMarker.COPIED}")

        try:
            # Skip if required marker not found
            if (not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.CREATED) or 
                not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.DELETED) or 
                not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.REVIEWED) or 
                not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.CLEANED)
                ):
                logger.warning(f"{FileMarker.CREATED} or {FileMarker.DELETED} or {FileMarker.REVIEWED} or {FileMarker.CLEANED} marker not found, Resource not ready : {resource_name}, skipping")
                skipped_count += 1
                continue
            elif explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.COPIED) and not re_run:
                # This marker indicate the resource has been processsed previously, skipping
                logger.info(f"Marker found: {FileMarker.COPIED} - Skipping resource: {resource_name}, remove this marker manually if required")
                skipped_count += 1
                continue
            logger.info(f"Processing resource: {resource_name}")

            # Copy the main.tf to the `/output/examples/resources/{resource_name}`
            explorer.copy_file(
                source_file=os.path.join(dir_path, "main.tf"),
                destination_file=os.path.join(target_local_dir, "examples/resources", resource_name, "main.tf"),
                logger=logger,
                replace=True
            )

            # Create a new template to `/output/examples/resources/{resource_name}`
            summary_text_path = os.path.join(source_local_dir, resource_name, "summary.txt")
            logger.info(f"Reading summary.txt from {summary_text_path}")
            summary_text = explorer.read_text_file(file_path=summary_text_path, logger=logger)
            logger.debug(f"Summary text: {summary_text}")

            if summary_text:
                explorer.create_template(
                    resource_name=short_resource_name,
                    summary_text=summary_text,
                    directory_path=os.path.join(target_local_dir, "templates/resources"),
                    logger=logger,
                    replace=True
                    )
                explorer.create_marker(dir_path=dir_path, marker_type=FileMarker.COPIED, logger=logger)
                successful_count += 1
            else:
                logger.error(f"Unable to read summary.txt for resource: {resource_name}")
                failed_count += 1
        
        except Exception as e:
            logger.error(f"Error processing resource {resource_name}: {str(e)}")
            failed_count += 1
        finally:
            logger.info(f"##################### END : {resource_name} #############################")

    source_upload_result = upload_to_s3_prefix(
        bucket_name=source_bucket_name,
        local_directory=source_local_dir,
        exclude_patterns=[
            ".terraform/*"
        ],
        logger=logger
    )

    target_upload_result = upload_to_s3_prefix(
        bucket_name=target_bucket_name,
        s3_prefix=target_bucket_prefix,
        local_directory=target_local_dir,
        exclude_patterns=[
            ".terraform/*"
        ],
        logger=logger
    )

    # After the loop completes, log the summary
    logger.info("=== Processing Summary ===")
    logger.info(f"Total resources: {total_count}")
    if total_count > 0:
        logger.info(f"Successfully processed: {successful_count} ({(successful_count/total_count)*100:.1f}%)")
        logger.info(f"Skipped: {skipped_count} ({(skipped_count/total_count)*100:.1f}%)")
        logger.info(f"Failed: {failed_count} ({(failed_count/total_count)*100:.1f}%)")
    logger.info("=======================")

def write_artifact(
    target_resources_dir: list, 
    logger: logging.Logger,
    re_run: bool = False
    ):

    # Initialize counters at the start
    successful_count = 0
    skipped_count = 0
    failed_count = 0
    total_count = len(target_resources_dir)

    for dir_path in sorted(target_resources_dir):
        resource_name = dir_path.split("/")[-1]
        short_resource_name = resource_name.split("awscc_")[1]

        logger.info(f"##################### START : {resource_name} #############################")
        logger.info(f"Action type: {FileMarker.COPIED}")

        try:
            # Skip if required marker not found
            if (not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.CREATED) or 
                not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.DELETED) or 
                not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.REVIEWED) or 
                not explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.CLEANED)
                ):
                logger.warning(f"{FileMarker.CREATED} or {FileMarker.DELETED} or {FileMarker.REVIEWED} or {FileMarker.CLEANED} marker not found, Resource not ready : {resource_name}, skipping")
                skipped_count += 1
                continue
            elif explorer.check_if_dir_contains_marker(dir_path=dir_path, marker_type=FileMarker.COPIED) and not re_run:
                # This marker indicate the resource has been processsed previously, skipping
                logger.info(f"Marker found: {FileMarker.COPIED} - Skipping resource: {resource_name}, remove this marker manually if required")
                skipped_count += 1
                continue
            logger.info(f"Processing resource: {resource_name}")

            # Copy the main.tf to the `/output/examples/resources/{resource_name}`
            explorer.copy_file(
                source_file=os.path.join(dir_path, "main.tf"),
                destination_file=os.path.join(os.getcwd(), "output/examples/resources", resource_name, "main.tf"),
                logger=logger,
                replace=True
            )

            # Create a new template to `/output/examples/resources/{resource_name}`
            summary_text_path = os.path.join(os.getcwd(), "target_resources/examples/resources", resource_name, "summary.txt")
            logger.info(f"Reading summary.txt from {summary_text_path}")
            summary_text = explorer.read_text_file(file_path=summary_text_path, logger=logger)
            logger.debug(f"Summary text: {summary_text}")

            if summary_text:
                explorer.create_template(
                    resource_name=short_resource_name,
                    summary_text=summary_text,
                    directory_path=os.path.join(os.getcwd(), "output/templates/resources"),
                    logger=logger,
                    replace=True
                    )
                explorer.create_marker(dir_path=dir_path, marker_type=FileMarker.COPIED, logger=logger)
                successful_count += 1
            else:
                logger.error(f"Unable to read summary.txt for resource: {resource_name}")
                failed_count += 1
        
        except Exception as e:
            logger.error(f"Error processing resource {resource_name}: {str(e)}")
            failed_count += 1
            
        finally:
            logger.info(f"##################### END : {resource_name} #############################")

    # After the loop completes, log the summary
    logger.info("=== Processing Summary ===")
    logger.info(f"Total resources: {total_count}")
    logger.info(f"Successfully processed: {successful_count} ({(successful_count/total_count)*100:.1f}%)")
    logger.info(f"Skipped: {skipped_count} ({(skipped_count/total_count)*100:.1f}%)")
    logger.info(f"Failed: {failed_count} ({(failed_count/total_count)*100:.1f}%)")
    logger.info("=======================")

def start_inference(event, context):
    # Lambda always use /tmp for temporary files
    event["dir_path"] = f"/tmp/target_resources/{event["target_resource"]}"

    download_result = download_from_s3_prefix(
        bucket_name=os.environ.get("ASSETS_BUCKET"),
        prefix=event["target_resource"],
        local_directory=event["dir_path"],
        exclude_prefixes=[".terraform"],
        logger=logger
    )

    resource_event = {
        "target_resource": event["target_resource"],
        "dir_path": event["dir_path"],
        "per_inference_sleep": 5,
        "per_resource_sleep": 60, 
        "per_resource_timeout": 900,
        "re_run": False,
        "logger_level": tool_logger_level,
        "logger": logger,
    }

    match event["prompt_type"]:
        case "CREATE":  # Step 1
            resource_event["base_prompt"] = USER_PROMPT_CREATE
            resource_event["marker_type"] = FileMarker.CREATED
            next_prompt_type = "DELETE"
        case "DELETE": # Step 2
            resource_event["base_prompt"] = USER_PROMPT_DELETE
            resource_event["marker_type"] = FileMarker.DELETED
            next_prompt_type = "REVIEW"
        case "REVIEW": # Step 3
            resource_event["base_prompt"] = USER_PROMPT_REVIEW
            resource_event["marker_type"] = FileMarker.REVIEWED
            next_prompt_type = "CLEANER"
        case "CLEANER": # Step 4
            resource_event["base_prompt"] = USER_PROMPT_CLEANER
            resource_event["marker_type"] = FileMarker.CLEANED
            next_prompt_type = "SUMMARY"
        case "SUMMARY": # Step 5
            resource_event["base_prompt"] = USER_PROMPT_SUMMARY
            resource_event["marker_type"] = FileMarker.SUMMARY
            next_prompt_type = "COPY"

    logger.debug("Lambda payload contents:", resource_event)  # Debug print

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_resource(**resource_event, lambda_context=context))
        
        if explorer.check_if_dir_contains_marker(dir_path=resource_event["dir_path"], marker_type=resource_event["marker_type"]):
            logger.info("Loop completed successfully")
            resource_event["status"] = "SUCCESS"
            resource_event["prompt_type"] = next_prompt_type
        else:
            logger.info("Loop did not complete successfully")
            resource_event["status"] = "FAILED"
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        upload_result = upload_to_s3_prefix(
            bucket_name=os.environ.get("ASSETS_BUCKET"),
            s3_prefix=event["target_resource"],
            local_directory=event["dir_path"],
            exclude_patterns=[
                ".terraform/*"
            ],
            logger=logger
        )
        
        logger.info("End : AWSCC Doc using Anthropic Computer Use")
        loop.close()
        resource_event.pop("logger")
        resource_event.pop("base_prompt")
        return resource_event

def lambda_handler(event, context):
    # TODO: Pin to us-west-2 for the best performance
    os.environ["AWS_REGION"] = "us-west-2"

    logger.info("Starting : AWSCC Doc using Anthropic Computer Use")
    logger.debug("Event contents:", event)  # Debug print
    
    if "prompt_type" in event and event["prompt_type"] in ["CREATE", "DELETE", "UPDATE", "REVIEW", "CLEANER", "SUMMARY"]:
        result_event = start_inference(event, context)
        
    elif "prompt_type" in event and event["prompt_type"] == "COPY":
        result_event = build_artifact(
            source_bucket_name=os.environ.get("ASSETS_BUCKET"),
            target_bucket_name=os.environ.get("ARTIFACTS_BUCKET"),
            target_bucket_prefix=context.aws_request_id,
            target_resources=event["target_resources"],
            re_run=True,
            logger=logger)
    else:
        result_event = {
            "status": "FAILED",
            "message": "Invalid prompt type"
        }
    return result_event
    
if __name__ == "__main__":
        
    print("Starting : Main thread")

    # Get target resource from command line argument
    if len(sys.argv) < 2:
        print("Please provide target resource as command line argument")
        sys.exit(1)
    
    # Loop through resources
    prompt_type = sys.argv[1]
    target_resource = sys.argv[2]

    # Pin to us-west-2 for better throughput 
    # os.environ["AWS_REGION"] = "us-west-2"

    # Create a temporary working dir
    # TODO : download from persistent storage like S3
    dir_path = explorer.create_directory(
        base_path=os.getcwd(),
        directory_name=os.path.join(os.getcwd(), "target_resources", target_resource),
        logger=logger
        )

    lambda_event = {
        "target_resource": target_resource,
        "dir_path": dir_path,
        "per_inference_sleep": 5,
        "per_resource_sleep": 60, 
        "per_resource_timeout": 900,
        "re_run": False, # set this True only if you want to re-create all resources
        "logger_level": tool_logger_level
    }

    match prompt_type:
        case "CREATE":  # Step 1
            lambda_event["base_prompt"] = USER_PROMPT_CREATE
            lambda_event["marker_type"] = FileMarker.CREATED
        case "DELETE": # Step 2
            lambda_event["base_prompt"] = USER_PROMPT_DELETE
            lambda_event["marker_type"] = FileMarker.DELETED
        case "REVIEW": # Step 3
            lambda_event["base_prompt"] = USER_PROMPT_REVIEW
            lambda_event["marker_type"] = FileMarker.REVIEWED
        case "CLEANER": # Step 4
            lambda_event["base_prompt"] = USER_PROMPT_CLEANER
            lambda_event["marker_type"] = FileMarker.CLEANED
        case "SUMMARY": # Step 5
            lambda_event["base_prompt"] = USER_PROMPT_SUMMARY
            lambda_event["marker_type"] = FileMarker.SUMMARY
        
    lambda_handler(event=lambda_event, context=None)

    """    
    match prompt_type:
        case "COPY": # Step 6
            prep_files(
                target_resources_dir=target_resources_dir,
                re_run=True,
                logger=logger)
    """