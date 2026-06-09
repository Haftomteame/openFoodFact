# Lance backend + frontend dans un seul terminal
Set-Location $PSScriptRoot

if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker compose up -d 2>$null
}

npm run dev
