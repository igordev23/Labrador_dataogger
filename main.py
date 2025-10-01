import time
from datetime import datetime
from periphery import I2C

# ---------------- CONFIG ----------------
INTERVAL_SEC = 1
SD_CARD = "/media/caninos/adata64"
DATALOGGER = "/data.txt"

# ---------------- AHT10 (I2C-2) ----------------
AHT10_BUS = "/dev/i2c-2"
AHT10_ADDRESS = 0x38
i2c_aht10 = I2C(AHT10_BUS)

# ---------------- VL53L0X (I2C-3) ----------------
VL53L0X_BUS = "/dev/i2c-3"
VL53L0X_ADDRESS = 0x29
i2c_vl53 = I2C(VL53L0X_BUS)


# ---------------- FUNÇÕES AHT10 ----------------
def aht10_init():
    i2c_aht10.transfer(AHT10_ADDRESS, [I2C.Message([0xBE, 0x08, 0x00], read=False)])
    time.sleep(0.5)

def aht10_measure():
    i2c_aht10.transfer(AHT10_ADDRESS, [I2C.Message([0xAC, 0x33, 0x00], read=False)])
    time.sleep(0.5)

def aht10_read():
    msg = I2C.Message([0x00]*6, read=True)
    i2c_aht10.transfer(AHT10_ADDRESS, [msg])
    return msg.data

def aht10_data(data):
    humidity = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4)) * 100 / (1 << 20)
    temperature = (((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]) * 200 / (1 << 20) - 50
    return humidity, temperature


# ---------------- FUNÇÕES VL53L0X ----------------
def vl53l0x_init():
    # Sequência básica de reset
    i2c_vl53.transfer(VL53L0X_ADDRESS, [I2C.Message([0x88, 0x00], read=False)])
    i2c_vl53.transfer(VL53L0X_ADDRESS, [I2C.Message([0x80, 0x01], read=False)])
    i2c_vl53.transfer(VL53L0X_ADDRESS, [I2C.Message([0xFF, 0x01], read=False)])
    i2c_vl53.transfer(VL53L0X_ADDRESS, [I2C.Message([0x00, 0x00], read=False)])
    time.sleep(0.5)
    # Start continuous mode
    i2c_vl53.transfer(VL53L0X_ADDRESS, [I2C.Message([0x00, 0x02], read=False)])
    time.sleep(0.01)

def vl53l0x_read_distance():
    # Lê RESULT_RANGE_STATUS (0x14)
    i2c_vl53.transfer(VL53L0X_ADDRESS, [I2C.Message([0x14], read=False)])
    msg = I2C.Message([0x00]*12, read=True)
    i2c_vl53.transfer(VL53L0X_ADDRESS, [msg])
    dist = (msg.data[10] << 8) | msg.data[11]
    return dist


# ---------------- MAIN ----------------
def main():
    print("Iniciando monitoramento AHT10 + VL53L0X!\n")

    # Cria arquivo se não existir
    try:
        with open(SD_CARD + DATALOGGER, "x") as f:
            f.write("data_hora,umidade_percentual,temperatura_celsius,distancia_mm\n")
    except FileExistsError:
        print("Arquivo já existe. Novos dados serão acrescidos.\n")

    # Inicializa sensores separadamente
    aht10_init()
    vl53l0x_init()

    print("data_hora,umidade_percentual,temperatura_celsius,distancia_mm")

    try:
        with open(SD_CARD + DATALOGGER, "a") as f:
            while True:
                timestamp = datetime.now()

                # ---------------- AHT10 ----------------
                aht10_measure()
                hum, temp = aht10_data(aht10_read())

                # ---------------- VL53L0X ----------------
                dist = vl53l0x_read_distance()

                # Print no terminal
                print(f"{timestamp},{hum:.2f},{temp:.2f},{dist}")

                # Grava no arquivo
                f.write(f"{timestamp},{hum:.2f},{temp:.2f},{dist}\n")
                f.flush()  # garante escrita imediata no SD

                time.sleep(INTERVAL_SEC)

    except KeyboardInterrupt:
        i2c_aht10.close()
        i2c_vl53.close()
        print("\nFinalizando monitoramento!\n")


if __name__ == "__main__":
    main()
