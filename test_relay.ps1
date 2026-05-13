# Script para probar el Relé USB (LCUS-1 / CH340) en Windows
# Este script activa el relé dos veces para verificar su funcionamiento físico.

$ErrorActionPreference = "Stop"

function Test-Relay {
    param (
        [string]$PortName = ""
    )

    # Si no se especifica puerto, intentamos encontrar el CH340 automáticamente
    if (-not $PortName) {
        Write-Host "🔍 Buscando dispositivo CH340..." -ForegroundColor Cyan
        $dev = Get-PnpDevice -PresentOnly | Where-Object { $_.FriendlyName -like "*CH340*" -or $_.FriendlyName -like "*USB-SERIAL*" } | Select-Object -First 1
        
        if ($dev) {
            # Extraer el COM port del nombre amigable (ej: "USB-SERIAL CH340 (COM4)")
            if ($dev.FriendlyName -match "\((COM\d+)\)") {
                $PortName = $Matches[1]
                Write-Host "✅ Encontrado en puerto: $PortName" -ForegroundColor Green
            }
        }
    }

    if (-not $PortName) {
        Write-Host "❌ No se encontró el relé automáticamente." -ForegroundColor Red
        Write-Host "Por favor, verifica el Administrador de Dispositivos y ejecuta el script indicando el puerto:"
        Write-Host "Ejemplo: .\test_relay.ps1 -PortName COM4"
        return
    }

    $serial = New-Object System.IO.Ports.SerialPort($PortName, 9600, "None", 8, "One")
    
    try {
        Write-Host "🔌 Abriendo puerto $PortName..."
        $serial.Open()

        # Comandos hexadecimales LCUS-1
        $cmdOn  = [byte[]](0xA0, 0x01, 0x01, 0xA2)
        $cmdOff = [byte[]](0xA0, 0x01, 0x00, 0xA1)

        for ($i = 1; $i -le 2; $i++) {
            Write-Host "🔔 Click #$i: Encendiendo..." -NoNewline -ForegroundColor Yellow
            $serial.Write($cmdOn, 0, $cmdOn.Length)
            Start-Sleep -Milliseconds 800
            
            Write-Host " Apagando." -ForegroundColor Gray
            $serial.Write($cmdOff, 0, $cmdOff.Length)
            
            if ($i -lt 2) { Start-Sleep -Seconds 1 }
        }

        Write-Host "`n✨ Prueba completada con éxito." -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Error al comunicarse con el puerto $PortName : $($_.Exception.Message)" -ForegroundColor Red
    }
    finally {
        if ($serial.IsOpen) {
            $serial.Close()
            Write-Host "🔌 Puerto cerrado."
        }
    }
}

# Ejecutar la prueba
Test-Relay
