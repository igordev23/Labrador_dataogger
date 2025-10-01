import time
from datetime import datetime
from periphery import I2C

# Intervalo de leitura (segundos)
INTERVAL_SEC = 1

# Caminho do arquivo
SD_CARD = "/media/caninos/adata64"
DATALOGGER = "/data.txt"

# AHT10 config
I2C_2_BUS = "/dev/i2c-2"
I2C_2_ADDRESS = 0x38
i2c_2 = I2C(I2C_2_BUS)

def aht10_init():
    """
    Inicializa o sensor AHT10.
    """
    init_command = [0xBE, 0x08, 0x00]
    i2c_2.transfer(I2C_2_ADDRESS, [I2C.Message(init_command)])
    time.sleep(0.5)

def aht10_measure():
    """
    Solicita medição ao AHT10.
    """
    measure_command = [0xAC, 0x33, 0x00]
    i2c_2.transfer(I2C_2_ADDRESS, [I2C.Message(measure_command)])
    time.sleep(0.5)

def aht10_read():
    """
    Lê os 6 bytes de dados do AHT10.
    """
    read_command = I2C.Message([0x00] * 6, read=True)
    i2c_2.transfer(I2C_2_ADDRESS, [read_command])
    return read_command.data

def aht10_data(data):
    """
    Converte os bytes em umidade (%) e temperatura (°C).
    """
    humidity = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4)) * 100 / (1 << 20)
    temperature = (((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]) * 200 / (1 << 20) - 50
    return humidity, temperature

def main():
    print("Iniciando monitoramento do AHT10!\n")

    try:
        with open(SD_CARD + DATALOGGER, "x") as f:
            f.write("data_hora,umidade_percentual,temperatura_celsius\n")
    except FileExistsError:
        print("Arquivo já existe. Novos dados serão acrescidos.\n")

    aht10_init()

    print("data_hora,umidade_percentual,temperatura_celsius")

    try:
        while True:
            timestamp = datetime.now()
            aht10_measure()
            hum, temp = aht10_data(aht10_read())

            print(f"{timestamp},{hum:.2f},{temp:.2f}")

            with open(SD_CARD + DATALOGGER, "a") as f:
                f.write(f"{timestamp},{hum:.2f},{temp:.2f}\n")

            time.sleep(INTERVAL_SEC)

    except KeyboardInterrupt:
        i2c_2.close()
        print("\nFinalizando monitoramento!\n")

if __name__ == "__main__":
    main()
