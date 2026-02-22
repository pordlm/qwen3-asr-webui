Write-Host ">>> Starting Qwen3-ASR Container Deployment..."

# 1. Configuration
$WorkspacePath = (Get-Location).Path
$ImageName = "qwenllm/qwen3-asr:latest"
$ContainerName = "qwen3-asr"
$HostPort = 8000
$ContainerPort = 80

# 2. Cleanup old container
Write-Host "Checking for existing container..."
if (docker ps -a --format '{{.Names}}' | Select-String -Quiet "^$ContainerName$") {
    Write-Host "Removing old container: $ContainerName"
    docker rm -f $ContainerName
} else {
    Write-Host "No old container found. Continuing..."
}

# 3. Build and Run Docker Command
Write-Host "Launching container (First run will invoke pull, please wait)..."
Write-Host "Mounting: $WorkspacePath -> /data/shared/Qwen3-ASR"
Write-Host "Port Map: Local $HostPort -> Container $ContainerPort"

# Note: Using --gpus all for NVIDIA support
# Using --shm-size=4gb as recommended for large models
docker run --gpus all --name $ContainerName `
    -v /var/run/docker.sock:/var/run/docker.sock `
    -p "${HostPort}:${ContainerPort}" `
    --mount type=bind,source="$WorkspacePath",target=/data/shared/Qwen3-ASR `
    --shm-size=4gb `
    -it $ImageName

# 4. End status
if ($?) {
    Write-Host "`n>>> Container Session Ended."
    Write-Host "To restart/re-enter, run: docker start $ContainerName; docker exec -it $ContainerName bash"
} else {
    Write-Error "Container failed to start."
    Write-Host "Tip: If download is slow/stuck, you may need a Docker Registry Mirror."
}
