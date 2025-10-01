import time
from datetime import datetime
from periphery import I2C
import vl53l0x  # Biblioteca oficial VL53L0X

# Intervalo de leitura (segundos)
INTERVAL_SEC = 1

# Caminho do arquivo
SD_CARD = "/media/caninos/adata64"
DATALOGGER = "/data.txt"

# ---------------- AHT10 CONFIG (I2C-2) ----------------
AHT10_BUS = "/dev/i2c-2"
AHT10_ADDRESS = 0x38
i2c_aht10 = I2C(AHT10_BUS)

# ---------------- VL53L0X CONFIG ----------------
VL53L0X_BUS = 3  # Barramento I2C (como parâmetro para a biblioteca vl53l0x)

# ---------------- AHT10 ----------------
def aht10_init():
    init_command = [0xBE, 0x08, 0x00]
    i2c_aht10.transfer(AHT10_ADDRESS, [I2C.Message(init_command)])
    time.sleep(0.5)

def aht10_measure():
    measure_command = [0xAC, 0x33, 0x00]
    i2c_aht10.transfer(AHT10_ADDRESS, [I2C.Message(measure_command)])
    time.sleep(0.5)

def aht10_read():
    read_command = I2C.Message([0x00] * 6, read=True)
    i2c_aht10.transfer(AHT10_ADDRESS, [read_command])
    return read_command.data

def aht10_data(data):
    humidity = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4)) * 100 / (1 << 20)
    temperature = (((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]) * 200 / (1 << 20) - 50
    return humidity, temperature

# ---------------- MAIN ----------------
def main():
    print("Iniciando monitoramento AHT10 + VL53L0X!\n")

    try:
        with open(SD_CARD + DATALOGGER, "x") as f:
            f.write("data_hora,umidade_percentual,temperatura_celsius,distancia_mm\n")
    except FileExistsError:
        print("Arquivo já existe. Novos dados serão acrescidos.\n")

    # Inicializa sensores
    aht10_init()
    tof = vl53l0x.VL53L0X(bus=VL53L0X_BUS)  # Inicializa VL53L0X
    tof.start_ranging()

    print("data_hora,umidade_percentual,temperatura_celsius,distancia_mm")

    try:
        while True:
            timestamp = datetime.now()

            # AHT10
            aht10_measure()
            hum, temp = aht10_data(aht10_read())

            # VL53L0X
            dist = tof.get_distance()

            # Print no terminal
            print(f"{timestamp},{hum:.2f},{temp:.2f},{dist}")

            # Grava no arquivo
            with open(SD_CARD + DATALOGGER, "a") as f:
                f.write(f"{timestamp},{hum:.2f},{temp:.2f},{dist}\n")

            time.sleep(INTERVAL_SEC)

    except KeyboardInterrupt:
        tof.stop_ranging()
        i2c_aht10.close()
        print("\nFinalizando monitoramento!\n")

if __name__ == "__main__":
    main()
