# test-local.ps1
$venv = ".venv-test"
$pyproject_hash = (Get-FileHash pyproject.toml).Hash

if (!(Test-Path "$venv/pyproject.hash") -or
    (Get-Content "$venv/pyproject.hash") -ne $pyproject_hash) {

    Write-Host "pyproject.toml changed → fresh install" -ForegroundColor Yellow
    if (Test-Path $venv) { Remove-Item -Recurse -Force $venv }

    python -m venv $venv
    & "$venv\Scripts\pip.exe" install --upgrade pip -q
    & "$venv\Scripts\pip.exe" install -e ".[test]"

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Dependency-Installation fehlgeschlagen!"
        exit 1
    }

    Set-Content "$venv/pyproject.hash" $pyproject_hash
    Write-Host "Fresh install complete" -ForegroundColor Green
}
else {
    Write-Host "Using cached venv (pyproject.toml unchanged)" -ForegroundColor Green
}

& "$venv\Scripts\pytest.exe" tests/ -v --cov=custom_components.shabman --cov-report=term-missing
