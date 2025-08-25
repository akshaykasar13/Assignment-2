name: CI (Self-Hosted -> Dashboard)

on:
  push:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      force_fail:
        description: 'Force the job to fail (true/false)'
        type: choice
        options: [ "true", "false" ]
        default: "true"

permissions:
  contents: read

env:
  PIPELINE_NAME: ${{ github.workflow }}
  BRANCH: ${{ github.ref_name }}
  COMMIT: ${{ github.sha }}
  ACTOR: ${{ github.actor }}

jobs:
  build:
    # Your self-hosted Windows runner
    runs-on: [self-hosted, Windows]

    defaults:
      run:
        shell: powershell  # <- use Windows PowerShell, not pwsh

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Mark start time
        run: |
          $ts = [int]([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())
          "START_TS=$ts" | Out-File -FilePath $env:GITHUB_ENV -Append

      - name: Probe dashboard health
        env:
          DASHBOARD_URL: ${{ secrets.DASHBOARD_URL }}
        run: |
          if (-not $env:DASHBOARD_URL) {
            Write-Error "DASHBOARD_URL secret not set. Set it to http://localhost:8000 for a self-hosted runner."
            exit 1
          }
          Write-Host "Probing $env:DASHBOARD_URL/health"
          $r = Invoke-RestMethod -Method Get -Uri "$env:DASHBOARD_URL/health"
          Write-Host "Health OK:" ($r | ConvertTo-Json -Depth 4)

      - name: Do some work
        run: |
          Write-Host "Running simple step on self-hosted runner..."
          Start-Sleep -Seconds 3

      - name: Fail intentionally (for testing)
        if: ${{ github.event.inputs.force_fail == 'true' }}
        run: exit 1

      - name: Notify dashboard (always)
        if: ${{ always() }}
        env:
          DASHBOARD_URL: ${{ secrets.DASHBOARD_URL }}
          JOB_STATUS: ${{ job.status }}
        run: |
          $end = [int]([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())
          $dur = $end - [int]$env:START_TS
          $startIso  = [DateTimeOffset]::FromUnixTimeSeconds([int]$env:START_TS).UtcDateTime.ToString("o")
          $finishIso = [DateTimeOffset]::FromUnixTimeSeconds($end).UtcDateTime.ToString("o")
          $status = if ($env:JOB_STATUS -eq "success") { "success" } else { "failure" }

          $body = @{
            pipeline     = "${{ github.workflow }}"
            status       = $status
            duration_sec = $dur
            started_at   = $startIso
            finished_at  = $finishIso
            branch       = "${{ github.ref_name }}"
            commit       = "${{ github.sha }}"
            triggered_by = "${{ github.actor }}"
          } | ConvertTo-Json -Depth 10

          Write-Host "POST -> $env:DASHBOARD_URL/api/events/run"
          Write-Host $body
          $resp = Invoke-RestMethod -Method Post -Uri "$env:DASHBOARD_URL/api/events/run" -ContentType "application/json" -Body $body
          Write-Host "Ingest OK:" ($resp | ConvertTo-Json -Depth 10)
