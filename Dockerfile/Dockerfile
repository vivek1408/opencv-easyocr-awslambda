ARG FUNCTION_DIR="/function"
FROM python:3.8.12-slim as build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Install aws-lambda-cpp build dependencies
RUN apt-get update && \
  apt-get install -y \
  g++ \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev

# Copy function code
RUN mkdir -p ${FUNCTION_DIR}
COPY app/requirements.txt ${FUNCTION_DIR}/
RUN pip install -r ${FUNCTION_DIR}/requirements.txt --target ${FUNCTION_DIR} --no-cache-dir


# Install the function's dependencies
RUN pip install --target ${FUNCTION_DIR} awslambdaric

FROM python:3.8.12-slim
ARG FUNCTION_DIR
RUN apt-get update
RUN apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender1 unzip
WORKDIR ${FUNCTION_DIR}
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
ADD https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/english_g2.zip /opt/models/
ADD https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/japanese_g2.zip /opt/models/
ADD https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/craft_mlt_25k.zip /opt/models/
WORKDIR /opt/models/
RUN unzip english_g2
RUN unzip japanese_g2
RUN unzip craft_mlt_25k
WORKDIR ${FUNCTION_DIR}
COPY app/* ${FUNCTION_DIR}/
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "app.lambda_handler" ]
