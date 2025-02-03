FROM public.ecr.aws/lambda/python:3.12

# checkov:skip=CKV_DOCKER_1
RUN dnf update -y && dnf install -y \
    gcc \
    gcc-c++ \
    make \
    unzip \
    git \
    shadow-utils \
    sudo \
    && dnf clean all \
    && rm -rf /var/cache/dnf

RUN curl -fsSL https://releases.hashicorp.com/terraform/1.6.6/terraform_1.6.6_linux_arm64.zip -o terraform.zip \
    && unzip terraform.zip \
    && mv terraform /usr/local/bin/ \
    && rm terraform.zip

WORKDIR ${LAMBDA_TASK_ROOT}

COPY ./lib ./lib

COPY ./requirements.txt ./requirements.txt
    
RUN python -m pip install --no-cache-dir -r ./requirements.txt

# Env vars expected by Antrhopic Computer Use libraries
ENV DISPLAY_NUM=1
ENV HEIGHT=768
ENV WIDTH=1024
ENV API_PROVIDER=bedrock

ENV PYTHONPATH="${LAMBDA_TASK_ROOT}"
CMD [ "lib.awscc_tool_use.lambda_handler" ]

# checkov:skip=CKV_DOCKER_2:using lambda python runtime
# checkov:skip=CKV_DOCKER_3:using lambda python runtime