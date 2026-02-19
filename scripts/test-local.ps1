# test-local.ps1
$venv = ".venv-test"

if (Test-Path $venv) {
    Remove-Item -Recurse -Force $venv
}

python -m venv $venv
& "$venv\Scripts\pip.exe" install --upgrade pip -q
& "$venv\Scripts\pip.exe" install -e ".[test]"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Dependency-Installation fehlgeschlagen!"
    exit 1
}

& "$venv\Scripts\pytest.exe" tests/ -v --cov=custom_components.shabman --cov-report=term-missing
