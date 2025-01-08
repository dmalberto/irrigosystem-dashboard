#!/bin/bash

# Configurações básicas
IMAGE_NAME="irrigosystem-dash"
CONTAINER_NAME="irrigosystem-dash-container"
ECR_URL="767398063645.dkr.ecr.us-east-1.amazonaws.com"
AWS_REGION="us-east-1"
CLUSTER_ARN="arn:aws:ecs:us-east-1:767398063645:cluster/irrigosystem-dash"
SERVICE_ARN="arn:aws:ecs:us-east-1:767398063645:service/irrigosystem-dash/irrigosystem-dash-service"
EXECUTION_ROLE_ARN="arn:aws:iam::767398063645:role/ecsTaskExecutionRole"
LOG_GROUP="/ecs/irrigosystem-dash-task"
VERSION_FILE="version.json"

# Funções
authenticate_ecr() {
    echo "Autenticando no Amazon ECR..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URL
}

get_version() {
    if [ ! -f "$VERSION_FILE" ]; then
        echo "{\"version\": \"v0.0.0\"}" > $VERSION_FILE
    fi
    jq -r '.version' $VERSION_FILE
}

increment_version() {
    local current_version=$(get_version)
    local major=$(echo $current_version | cut -d'.' -f1 | sed 's/v//')
    local minor=$(echo $current_version | cut -d'.' -f2)
    local patch=$(echo $current_version | cut -d'.' -f3)
    local new_patch=$((patch + 1))
    echo "v${major}.${minor}.${new_patch}"
}

update_version() {
    local new_version=$1
    echo "{\"version\": \"$new_version\"}" > $VERSION_FILE
}

generate_task_definition() {
  NEW_IMAGE="$ECR_URL/$IMAGE_NAME:$new_version"
  echo "Gerando nova Task Definition com a imagem: $NEW_IMAGE"

  cat <<EOT > task-definition.json
{
    "family": "irrigosystem-dash-task",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024",
    "executionRoleArn": "$EXECUTION_ROLE_ARN",
    "containerDefinitions": [
        {
            "name": "$CONTAINER_NAME",
            "image": "$NEW_IMAGE",
            "cpu": 0,
            "essential": true,
            "portMappings": [
                {
                    "name": "${CONTAINER_NAME}-8501-tcp",
                    "containerPort": 8501,
                    "hostPort": 8501,
                    "protocol": "tcp",
                    "appProtocol": "http"
                }
            ],
            "environment": [],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "$LOG_GROUP",
                    "mode": "non-blocking",
                    "awslogs-create-group": "true",
                    "max-buffer-size": "25m",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "ecs"
                }
            },
            "systemControls": []
        }
    ]
}
EOT
}

register_task_definition() {
    echo "Registrando a nova Task Definition no ECS..."
    aws ecs register-task-definition --cli-input-json file://task-definition.json
}

update_ecs_service() {
    echo "Atualizando serviço no ECS para usar a nova Task Definition..."
    aws ecs update-service \
        --cluster $CLUSTER_ARN \
        --service $SERVICE_ARN \
        --force-new-deployment
}

# Fluxo principal
main() {
    # Incrementar a versão
    echo "Recuperando versão atual..."
    current_version=$(get_version)
    echo "Versão atual: $current_version"
    new_version=$(increment_version)
    echo "Nova versão: $new_version"

    # Atualizar arquivo de versão
    update_version $new_version

    # Autenticar no ECR
    authenticate_ecr

    # Construir a imagem Docker
    echo "Construindo a imagem Docker com tag: $IMAGE_NAME:$new_version..."
    docker build -t $IMAGE_NAME:$new_version .

    # Tag da imagem para o ECR
    echo "Marcando a imagem para o ECR: $ECR_URL/$IMAGE_NAME:$new_version..."
    docker tag $IMAGE_NAME:$new_version $ECR_URL/$IMAGE_NAME:$new_version

    # Fazer o push para o ECR
    echo "Enviando a imagem para o ECR..."
    docker push $ECR_URL/$IMAGE_NAME:$new_version

    # Gerar nova Task Definition
    generate_task_definition

    # Registrar a nova Task Definition
    register_task_definition

    # Atualizar o Serviço no ECS
    update_ecs_service

    echo "Deploy concluído com sucesso! Nova versão: $new_version"
}

# Executar o fluxo principal
main
