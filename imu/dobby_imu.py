import time
import smbus
import numpy as np
import math

# need to add some prints in reset_mpu
# need to add calibration function for mag
# need to add function to change
# which is faster, referenicng a class attribute "accel_data" evrery time or return ax, ay, az??


# ********************************************************** #
#			MPU9250 class to use the imu sensor
#	Class variables:
#		1. x_scale = the scaling value of raw x data
#		2. x_data  = holds the raw x data
#		3. x_bias  = holds the bias values calculated	(mag_bias and gyro_bias calculation still left)
# 		4. mag_calibration = holds calibration data for magnetometer
#	Class methods:
#		1. MPU9250.init_imu() - the main init function
#		2. MPU9250.update()   - loads lates raw data into x_data
#		3. MPU9250.scale_rawdata() - scales raw data to physical units
#		4. MPU9250.is_data_ready() - checks if latest data is ready for read
# ********************************************************** #

class MPU9250:
#	defining class variables here	#
	a_scale = None
	g_scale = None
	m_scale = None
	mag_mode = None
	mag_calibration = np.zeros((3,)) # faster than list.. [0, 0, 0]
	mag_bias = np.zeros((3,))
	a_res = None
	g_res = None
	m_res = None
	accel_data = np.zeros((3,)) # faster than list.. [0, 0, 0]
	gyro_data = np.zeros((3,)) # faster than list.. [0, 0 ,0]
	mag_data = np.zeros((3,)) # faster than list.. [0, 0, 0]
	accel_bias = np.zeros((3,))
	gyro_bias = np.zeros((3,))

	ACCEL_2G = 0x00
	ACCEL_4G = 0x01
	ACCEL_8G = 0x02
	ACCEL_16G = 0x03

	GYRO_250DPS = 0X00
	GYRO_500DPS = 0X01
	GYRO_1000DPS = 0X02
	GYRO_2000DPS = 0X03

	MAG_14BITS = 0x00
	MAG_16BITS = 0x01

	MAG_100_HZ = 0x06
	MAG_8_HZ = 0x02

	__AK8963_ADDRESS   =  0x0C
	__AK8963_WHO_AM_I  =  0x00
	__AK8963_INFO      =  0x01
	__AK8963_ST1       =  0x02
	__AK8963_XOUT_L    =  0x03
	__AK8963_XOUT_H    =  0x04
	__AK8963_YOUT_L    =  0x05
	__AK8963_YOUT_H    =  0x06
	__AK8963_ZOUT_L    =  0x07
	__AK8963_ZOUT_H    =  0x08
	__AK8963_ST2       =  0x09
	__AK8963_CNTL      =  0x0A
	__AK8963_ASTC      =  0x0C
	__AK8963_I2CDIS    =  0x0F
	__AK8963_ASAX      =  0x10
	__AK8963_ASAY      =  0x11
	__AK8963_ASAZ      =  0x12
	__SELF_TEST_X_GYRO =  0x00
	__SELF_TEST_Y_GYRO =  0x01
	__SELF_TEST_Z_GYRO =  0x02

	#define X_FINE_GAIN      0x03
	#define Y_FINE_GAIN      0x04
	#define Z_FINE_GAIN      0x05
	#define XA_OFFSET_H      0x06
	#define XA_OFFSET_L_TC   0x07
	#define YA_OFFSET_H      0x08
	#define YA_OFFSET_L_TC   0x09
	#define ZA_OFFSET_H      0x0A
	#define ZA_OFFSET_L_TC   0x0B

	__SELF_TEST_X_ACCEL = 0x0D
	__SELF_TEST_Y_ACCEL = 0x0E
	__SELF_TEST_Z_ACCEL = 0x0F
	__SELF_TEST_A      =  0x10
	__XG_OFFSET_H      =  0x13
	__XG_OFFSET_L      =  0x14
	__YG_OFFSET_H      =  0x15
	__YG_OFFSET_L      =  0x16
	__ZG_OFFSET_H      =  0x17
	__ZG_OFFSET_L      =  0x18
	__SMPLRT_DIV       =  0x19
	__CONFIG           =  0x1A
	__GYRO_CONFIG      =  0x1B
	__ACCEL_CONFIG     =  0x1C
	__ACCEL_CONFIG2    =  0x1D
	__LP_ACCEL_ODR     =  0x1E
	__WOM_THR          =  0x1F
	__MOT_DUR          =  0x20
	__ZMOT_THR         =  0x21
	__ZRMOT_DUR        =  0x22
	__FIFO_EN          =  0x23
	__I2C_MST_CTRL     =  0x24
	__I2C_SLV0_ADDR    =  0x25
	__I2C_SLV0_REG     =  0x26
	__I2C_SLV0_CTRL    =  0x27
	__I2C_SLV1_ADDR    =  0x28
	__I2C_SLV1_REG     =  0x29
	__I2C_SLV1_CTRL    =  0x2A
	__I2C_SLV2_ADDR    =  0x2B
	__I2C_SLV2_REG     =  0x2C
	__I2C_SLV2_CTRL    =  0x2D
	__I2C_SLV3_ADDR    =  0x2E
	__I2C_SLV3_REG     =  0x2F
	__I2C_SLV3_CTRL    =  0x30
	__I2C_SLV4_ADDR    =  0x31
	__I2C_SLV4_REG     =  0x32
	__I2C_SLV4_DO      =  0x33
	__I2C_SLV4_CTRL    =  0x34
	__I2C_SLV4_DI      =  0x35
	__I2C_MST_STATUS   =  0x36
	__INT_PIN_CFG      =  0x37
	__INT_ENABLE       =  0x38
	__DMP_INT_STATUS   =  0x39
	__INT_STATUS       =  0x3A
	__ACCEL_XOUT_H     =  0x3B
	__ACCEL_XOUT_L     =  0x3C
	__ACCEL_YOUT_H     =  0x3D
	__ACCEL_YOUT_L     =  0x3E
	__ACCEL_ZOUT_H     =  0x3F
	__ACCEL_ZOUT_L     =  0x40
	__TEMP_OUT_H       =  0x41
	__TEMP_OUT_L       =  0x42
	__GYRO_XOUT_H      =  0x43
	__GYRO_XOUT_L      =  0x44
	__GYRO_YOUT_H      =  0x45
	__GYRO_YOUT_L      =  0x46
	__GYRO_ZOUT_H      =  0x47
	__GYRO_ZOUT_L      =  0x48
	__EXT_SENS_DATA_00 =  0x49
	__EXT_SENS_DATA_01 =  0x4A
	__EXT_SENS_DATA_02 =  0x4B
	__EXT_SENS_DATA_03 =  0x4C
	__EXT_SENS_DATA_04 =  0x4D
	__EXT_SENS_DATA_05 =  0x4E
	__EXT_SENS_DATA_06 =  0x4F
	__EXT_SENS_DATA_07 =  0x50
	__EXT_SENS_DATA_08 =  0x51
	__EXT_SENS_DATA_09 =  0x52
	__EXT_SENS_DATA_10 =  0x53
	__EXT_SENS_DATA_11 =  0x54
	__EXT_SENS_DATA_12 =  0x55
	__EXT_SENS_DATA_13 =  0x56
	__EXT_SENS_DATA_14 =  0x57
	__EXT_SENS_DATA_15 =  0x58
	__EXT_SENS_DATA_16 =  0x59
	__EXT_SENS_DATA_17 =  0x5A
	__EXT_SENS_DATA_18 =  0x5B
	__EXT_SENS_DATA_19 =  0x5C
	__EXT_SENS_DATA_20 =  0x5D
	__EXT_SENS_DATA_21 =  0x5E
	__EXT_SENS_DATA_22 =  0x5F
	__EXT_SENS_DATA_23 =  0x60
	__MOT_DETECT_STATUS = 0x61
	__I2C_SLV0_DO      = 0x63
	__I2C_SLV1_DO      = 0x64
	__I2C_SLV2_DO      = 0x65
	__I2C_SLV3_DO      = 0x66
	__I2C_MST_DELAY_CTRL = 0x67
	__SIGNAL_PATH_RESET  = 0x68
	__MOT_DETECT_CTRL  = 0x69
	__USER_CTRL        =  0x6A
	__PWR_MGMT_1       =  0x6B
	__PWR_MGMT_2       =  0x6C
	__DMP_BANK         =  0x6D
	__DMP_RW_PNT       =  0x6E
	__DMP_REG          =  0x6F
	__DMP_REG_1        =  0x70
	__DMP_REG_2        =  0x71
	__FIFO_COUNTH      =  0x72
	__FIFO_COUNTL      =  0x73
	__FIFO_R_W         =  0x74
	__WHO_AM_I_MPU9250 =  0x75
	__XA_OFFSET_H      =  0x77
	__XA_OFFSET_L      =  0x78
	__YA_OFFSET_H      =  0x7A
	__YA_OFFSET_L      =  0x7B
	__ZA_OFFSET_H      =  0x7D
	__ZA_OFFSET_L      =  0x7E
	__MPU9250_ADDRESS  =  0x68

	# choose the magnetometer sampling rate, 100Hz or 8Hz
	__MAG_MODE_100 = 0x06
	__MAG_MODE_8 = 0x02

	# choose full scale ranges of accel
	__AFS_2G = 0x00
	__AFS_4G = 0x01
	__AFS_8G = 0x02
	__AFS_16G = 0x03

	# choose full scale ranges of gyro
	__GFS_250DPS = 0X00
	__GFS_500DPS = 0X01
	__GFS_1000DPS = 0X02
	__GFS_2000DPS = 0X03

	# choose full scale ranges of magnetometer
	__MFS_14BITS = 0x00
	__MFS_16BITS = 0x01

	bus = smbus.SMBus(2)

	__MAGBIAS_X = 0
	__MAGBIAS_Y = 0
	__MAGBIAS_Z = 0

	__accel_bias_file = None

	def __init__(self, Ascale, Gscale, Mscale, magMode):

		if Ascale not in [self.__AFS_2G, self.__AFS_4G, self.__AFS_8G, self.__AFS_16G]:
			raise ValueError('ACCEL_SETTINGS: Incorrect accel scale chosen!\n')
			return False

		else:
			self.a_scale = Ascale

			if Gscale not in [self.__GFS_250DPS, self.__GFS_500DPS, self.__GFS_1000DPS, self.__GFS_2000DPS]:
				raise ValueError('GYRO_SETTINGS: Incorrect gyro scale chosen!\n')
				return False

			else:
				self.g_scale = Gscale

				if Mscale not in [self.__MFS_14BITS, self.__MFS_16BITS]:
					raise ValueError('MAG_SETTINGS: Incorrect mag scale chosen!\n')
					return False

				else:
					self.m_scale = Mscale

					if magMode not in [self.__MAG_MODE_100, self.__MAG_MODE_8]:
						raise ValueError('MAG_SETTINGS: Incorrect mag mode chosen!\n')
						return False

					else:
						self.mag_mode = magMode
						self.init_imu()
		# instead of putting scale functions
		# How about when we read_accel we store only after scaling?
		# modification done, have removed scale_rawdata()
		#---------------------------------------------------------------#

		# Why is there a accel_calibrate function apart from the calibrate?
		# yet to be made, need to calculate accel offsets by tilting quad on all axes
		#---------------------------------------------------------------#

		#added scale_rawdata function call it last in update function
		# removed scale_rawdata #

	def init_mpu(self):

		# wake up device
		self.bus.write_byte_data(self.__MPU9250_ADDRESS,self.__PWR_MGMT_1, 0X00)
		time.sleep(0.1)

		# get stable time source
		self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__PWR_MGMT_1, 0x01)

		self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__CONFIG, 0x03)
		self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__SMPLRT_DIV, 0x04)

		c = self.bus.read_byte_data(self.__MPU9250_ADDRESS, self.__GYRO_CONFIG)
		c = c & ~0x02
		c = c & ~0x18
		c = c | self.g_scale << 3
		self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__GYRO_CONFIG, c)

		c = self.bus.read_byte_data(self.__MPU9250_ADDRESS, self.__ACCEL_CONFIG)
		c = c & ~0x18
		c = c | self.a_scale << 3
		self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__ACCEL_CONFIG, c)

		c = self.bus.read_byte_data(self.__MPU9250_ADDRESS, self.__ACCEL_CONFIG2)
		c = c & ~0x0F
		c = c | 0x03
		self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__ACCEL_CONFIG2, c)

		self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__INT_PIN_CFG, 0x22)
		self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__INT_ENABLE, 0x01)

		return True

	def init_ak8963(self):

		self.bus.write_byte_data(self.__AK8963_ADDRESS, self.__AK8963_CNTL, 0x00)
		time.sleep(0.01)
		self.bus.write_byte_data(self.__AK8963_ADDRESS, self.__AK8963_CNTL, 0x0F)
		time.sleep(0.01)

		rawData = self.bus.read_i2c_block_data(self.__AK8963_ADDRESS, self.__AK8963_ASAX, 3)

		for i in range(3):
			self.mag_calibration[i] = float((rawData[i] - 128)/256.0 + 1.0)
			#i = i + 1 dont do this it will update itself

		self.bus.write_byte_data(self.__AK8963_ADDRESS, self.__AK8963_CNTL, 0x00)
		time.sleep(0.1)

		self.bus.write_byte_data(self.__AK8963_ADDRESS, self.__AK8963_CNTL, self.m_scale << 4 | self.mag_mode)
		time.sleep(0.1)

		return True

	def reset_mpu(self):

		self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__PWR_MGMT_1, 0x80)
		time.sleep(0.1)

	def read_accel(self):

		raw_data = self.bus.read_i2c_block_data(self.__MPU9250_ADDRESS, self.__ACCEL_XOUT_H, 6)

		self.accel_data[0] = self.dataConv(raw_data[1], raw_data[0])
		self.accel_data[1] = self.dataConv(raw_data[3], raw_data[2])
		self.accel_data[2] = self.dataConv(raw_data[5], raw_data[4])

	def read_gyro(self):

		raw_data = self.bus.read_i2c_block_data(self.__MPU9250_ADDRESS, self.__GYRO_XOUT_H, 6)

		self.gyro_data[0] = self.dataConv(raw_data[1], raw_data[0])
		self.gyro_data[1] = self.dataConv(raw_data[3], raw_data[2])
		self.gyro_data[2] = self.dataConv(raw_data[5], raw_data[4])

	def read_mag(self):

		if self.bus.read_byte_data(self.__AK8963_ADDRESS, self.__AK8963_ST1) & 0x01:
			raw_data = self.bus.read_i2c_block_data(self.__AK8963_ADDRESS, self.__AK8963_XOUT_L, 7)

			if (raw_data[6] & 0x08) != 0x08:
				self.mag_data[0] = self.dataConv(raw_data[1], raw_data[0])
				self.mag_data[1] = self.dataConv(raw_data[3], raw_data[2])
				self.mag_data[2] = self.dataConv(raw_data[5], raw_data[4])

	def get_ares(self):

		if self.a_scale == self.__AFS_2G:
			self.a_res = 2.0/32768.0

		elif self.a_scale == self.__AFS_4G:
			self.a_res = 4.0/32768.0

		elif self.a_scale == self.__AFS_8G:
			self.a_res = 8.0/32768.0

		elif self.a_scale == self.__AFS_16G:
			self.a_res = 16.0/32768.0

	def get_gres(self):

		if self.g_scale == self.__GFS_250DPS:
			self.g_res = 250.0/32768.0

		elif self.g_scale == self.__GFS_500DPS:
			self.g_res = 500.0/32768.0

		elif self.g_scale == self.__GFS_1000DPS:
			self.g_res = 1000.0/32768.0

		elif self.g_scale == self.__GFS_2000DPS:
			self.g_res = 2000.0/32768.0

	def get_mres(self):

		if self.m_scale == self.__MFS_14BITS:
			self.m_res = 4912.0/8190.0

		elif self.m_scale == self.__MFS_16BITS:
			self.m_res = 4912.0/32760.0

	def calibrate(self):
		accel_bias = np.zeros((3,))
		gyro_bias = np.zeros((3,))

		print "*************************************"
		print("\nThis program will generate a new gyro calibration file\n")
		print("keep your beaglebone very still for this procedure.\n")
		option = raw_input("Press Y to continue or anything else to quit\n")

		if option == 'Y':
			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__PWR_MGMT_1, 0x80)
			time.sleep(0.1)

			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__PWR_MGMT_1, 0x01)
			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__PWR_MGMT_2, 0x00)
			time.sleep(0.1)

			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__INT_ENABLE, 0x00)
			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__FIFO_EN, 0x00)
			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__PWR_MGMT_1, 0x00)
			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__I2C_MST_CTRL, 0x00)
			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__USER_CTRL, 0x00)
			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__USER_CTRL, 0x0C)
			time.sleep(0.015)

			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__CONFIG, 0x01)
			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__SMPLRT_DIV, 0x00)
			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__GYRO_CONFIG, 0x00)
			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__ACCEL_CONFIG, 0x00)

			gyrosensitivity  = 131
			accelsensitivity = 16384

			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__USER_CTRL, 0x40)
			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__FIFO_EN, 0x78)
			time.sleep(0.04)

			self.bus.write_byte_data(self.__MPU9250_ADDRESS, self.__FIFO_EN, 0x00)
			raw_data = self.bus.read_i2c_block_data(self.__MPU9250_ADDRESS, self.__FIFO_COUNTH, 2)
			fifo_count = self.dataConv(raw_data[1], raw_data[0])

			packet_count = fifo_count/12

			for i in range(packet_count):

				accel_temp = np.zeros((3,))
				gyro_temp = np.zeros((3,))
				temp_accel_bias = np.zeros((3,))
				temp_gyro_bias = np.zeros((3,))

				data = self.bus.read_i2c_block_data(self.__MPU9250_ADDRESS, self.__FIFO_R_W, 12)

				accel_temp[0] = self.dataConv(data[1], data[0])
				accel_temp[1] = self.dataConv(data[3], data[2])
				accel_temp[2] = self.dataConv(data[5], data[4])
				gyro_temp[0]  = self.dataConv(data[7], data[6])
				gyro_temp[1]  = self.dataConv(data[9], data[8])
				gyro_temp[2]  = self.dataConv(data[11], data[10])

				temp_accel_bias[0] += int(accel_temp[0])
				temp_accel_bias[1] += int(accel_temp[1])
				temp_accel_bias[2] += int(accel_temp[2])
				temp_gyro_bias[0]  += int(gyro_temp[0])
				temp_gyro_bias[1]  += int(gyro_temp[1])
				temp_gyro_bias[2]  += int(gyro_temp[2])

				#i = i + 1 dont do this it will update itself

			temp_accel_bias[0] /= int(packet_count)
			temp_accel_bias[1] /= int(packet_count)
			temp_accel_bias[2] /= int(packet_count)
			temp_gyro_bias[0]  /= int(packet_count)
			temp_gyro_bias[1]  /= int(packet_count)
			temp_gyro_bias[2]  /= int(packet_count)

			if accel_bias[2] > long(0):
				temp_accel_bias[2] -= int(accelsensitivity)

			else:
				temp_accel_bias[2] += int(accelsensitivity)

			#ata[0] = (-gyro_bias[0]/4  >> 8) & 0xFF
			#data[1] = (-gyro_bias[0]/4        & 0xFF
			#data[2] = (-gyro_bias[1]/4  >> 8) & 0xFF
			#data[3] = (-gyro_bias[1]/4        & 0xFF
			#ata[4] = (-gyro_bias[2]/4  >> 8) & 0xFF
			#data[5] = (-gyro_bias[2]/4        & 0xFF

			self.gyro_bias[0] = float(temp_gyro_bias[0])/float(gyrosensitivity)
			self.gyro_bias[1] = float(temp_gyro_bias[1])/float(gyrosensitivity)
			self.gyro_bias[2] = float(temp_gyro_bias[2])/float(gyrosensitivity)

			accel_bias_reg = np.zeros((3,1))
			raw_data = self.bus.read_i2c_block_data(self.__MPU9250_ADDRESS, self.__XA_OFFSET_H, 2)
			accel_bias_reg[0] = int(self.dataConv(raw_data[1], raw_data[0]))
			raw_data = self.bus.read_i2c_block_data(self.__MPU9250_ADDRESS, self.__YA_OFFSET_H, 2)
			accel_bias_reg[1] = int(self.dataConv(raw_data[1], raw_data[0]))
			raw_data = self.bus.read_i2c_block_data(self.__MPU9250_ADDRESS, self.__ZA_OFFSET_H, 2)
			accel_bias_reg[2] = int(self.dataConv(raw_data[1], raw_data[0]))

			# dont think this is needed neither is the above#
			#mask = (long)1
			#mask_bit = np.zeros((3,))

			#for i in range(3):
			#	if accel_bias_reg[i] & mask:
			#		 mask_bit[i] = 0x01

			#accel_bias_reg[0] -= (accel_bias[0]/8)
			#accel_bias_reg[1] -= (accel_bias[1]/8)
			#accel_bias_reg[2] -= (accel_bias[2]/8)

			self.accel_bias[0] = float(temp_accel_bias[0])/float(accelsensitivity)
			self.accel_bias[1] = float(temp_accel_bias[1])/float(accelsensitivity)
			self.accel_bias[2] = float(temp_accel_bias[2])/float(accelsensitivity)

		print "MPU calibration sequence finished\n"
		print "*************************************\n"


	def update(self):
		self.read_accel()
		self.read_gyro()
		self.read_mag()

	def calibrate_accel(self):
		accel_bias_calc = np.zeros((3,))
		data_1 = 0
		data_0 = 0

		print("********************************************\n")
		print("Initializing accelerometer calibration sequence..\n\r")
		#Is this function complete yet?
		#do ya think??
		time.sleep(2)
		print("You have to place the quadrotor in the specified position and then enter 1 to proceed:\n\r")
		time.sleep(2)
		print("Place quadrotor in nose up position...\n\r")
		next_step = input("Enter \"1\" to continue: ")
		if next_step == 1:
			for i in range(1000):
				self.read_accel()
				data_0 = data_0 + self.accel_data[0]
				if i%100 == 0:
					print ". ",
					time.sleep(0.1)
			data_0 = data_0/1000
			time.sleep(1)

			print("Place quadrotor in nose down position...\n\r")
			next_step = input("Enter \"1\" to continue: ")
			if next_step == 1:
				for i in range(1000):
					self.read_accel()
					data_1 = data_1 + self.accel_data[0]
					if i%100 == 0:
						print ". ",
						time.sleep(0.1)
				data_1 = data_1/1000
				time.sleep(1)

				#store in accel_bias[x]
				self.accel_bias[0] = 0.5*(data_1 + data_0)

				print("Place quadrotor on its right side...\n\r")
				next_step = input("Enter \"1\" to continue: ")
				if next_step == 1:
					for i in range(1000):
						self.read_accel()
						data_0 = data_0 + self.accel_data[1]
						if i%100 == 0:
							print ". ",
							time.sleep(0.1)
					data_0 = data_0/1000
					time.sleep(1)

					print("Place quadrotor on its left side...\n\r")
					next_step = input("Enter \"1\" to continue: ")
					if next_step == 1:
						for i in range(1000):
							self.read_accel()
							data_1 = data_1 + self.accel_data[1]
							if i%100 == 0:
								print ". ",
								time.sleep(0.1)
						data_1 = data_1/1000
						time.sleep(1)

						#store in accel_bias[y]
						self.accel_bias[1] = 0.5*(data_1 + data_0)

						print("Place quadrotor flat and right way up...\n\r")
						next_step = input("Enter \"1\" to continue: ")
						if next_step == 1:
							for i in range(1000):
								self.read_accel()
								data_0 = data_0 + self.accel_data[2]
								if i%100 == 0:
									time.sleep(0.1)
									print ". ",
							data_0 = data_0/1000
							time.sleep(1)

							print("Place quadrotor flat and on its back...\n\r")
							next_step = input("Enter \"1\" to continue: ")
							if next_step == 1:
								for i in range(1000):
									self.read_accel()
									data_1 = data_1 + self.accel_data[2]
									if i%100 == 0:
										print ". ",
										time.sleep(0.1)
								data_1 = data_1/1000
								time.sleep(1)

								#store in accel_bias[y]
								self.accel_bias[2] = 0.5*(data_1 + data_0)

								print("Accel calibration complete!\n\r")
								return self.save_accel_bias():



	def print_config(self):
		printf("Accelerometer sensitivity is ", self.a_res ," g \n\r");
		printf("Gyroscope sensitivity is ", self.g_res ," deg/s \n\r");
		printf("Magnetometer sensitivity is ", self.m_res," G \n\r");

		if self.mag_mode == self.__MFS_14BITS:
			print "Magnetometer resolution = 14  bits\n\r"

		elif self.mag_mode == self.__MFS_16BITS:
			print "Magnetometer resolution = 16  bits\n\r"

	def print_bias(self):
		print "x gyro bias = ", self.gyro_bias[0], "\n\r"
		print "y gyro bias = ", self.gyro_bias[1], "\n\r"
		print "z gyro bias = ", self.gyro_bias[2], "\n\r"
		print "x accel bias = ", self.accel_bias[0], "\n\r"
		print "y accel bias = ", self.accel_bias[1], "\n\r"
		print "z accel bias = ", self.accel_bias[2], "\n\r"

	def init_imu(self):
		## methods to be called during initialization of mpu ##
		# need to add error and exception handling
		who_am_i = int(self.bus.read_byte_data(self.__MPU9250_ADDRESS, self.__WHO_AM_I_MPU9250))

		if who_am_i == 113:
			print "MPU9250 is online...\n\r"
			time.sleep(1)
			self.reset_mpu()
			self.calibrate()
			if self.load_accel_bias() :
					time.sleep(2)
					self.print_bias()
					time.sleep(2)
					if self.init_mpu():
						print "MPU9250 initialized for active data mode....\n\r"
						if self.init_ak8963():
							print "Magnetometer activated for use.....\n\r"
							self.get_ares()
							self.get_gres()
							self.get_mres()
							time.sleep(3)
							print "MPU9250 initialization is over!\n\r"
							print "[ Ares Gres Mres ] = [ ", self.a_res, " ", self.g_res, " ", self.m_res, " ]"

						else:
							print("AK8963 not found!")
					else:
						print("MPU9250 init failed!")

			else:


		else:
			raise IOError("No MPU9250 found!\n")

	def set_default_config(self):
		self.a_scale = self.__AFS_4G
		self.g_scale = self.__GFS_1000DPS

	def dataConv(self, data1, data2):
		value = data1 | (data2 << 8)
		if(value & (1 << 16 - 1)):
			value -= (1<<16)
		return value

	def is_data_ready(self):
		drdy = self.bus.read_byte_data(self.__MPU9250_ADDRESS, self.__INT_STATUS)
		if drdy & 0x01:
			return True

		else:
			return False

	def scale_rawdata(self):
		self.accel_data[0] = float((self.accel_data[0] - self.accel_bias[0]) * self.a_res)
		self.accel_data[1] = float((self.accel_data[1] - self.accel_bias[1]) * self.a_res)
		self.accel_data[2] = float((self.accel_data[2] - self.accel_bias[2]) * self.a_res)

		self.mag_data[0] = float((self.mag_data[0] - self.mag_bias[0]) * self.m_res)
		self.mag_data[1] = float((self.mag_data[1] - self.mag_bias[1]) * self.m_res)
		self.mag_data[2] = float((self.mag_data[2] - self.mag_bias[2]) * self.m_res)

		self.gyro_data[0] = float((self.gyro_data[0] - self.gyro_bias[0]) * self.g_res)
		self.gyro_data[1] = float((self.gyro_data[1] - self.gyro_bias[1]) * self.g_res)
		self.gyro_data[2] = float((self.gyro_data[2] - self.gyro_bias[2]) * self.g_res)

	def load_accel_bias(self):

		try:
			self.__accel_bias_file =  open("accel_bias_save.txt", "r")
			response = input("The calibration data for accelerometer exists, do you want to recalibrate? Enter \"1\" to calibrate:")
			if response == 1:
				self.calibrate_accel()
				return True

			else:
				accel_bias_data = self.__accel_bias_file.readline()

		except IOError:
			print("The accelerometer needs calibration!")
			self.calibrate_accel()

	def save_accel_bias(self):
		self.__accel_bias_file = open("accel_bias_save.txt", "w")
		self.__accel_bias_file.write(self.accel_bias[0] + ',' + self.accel_bias[1] + ',' + self.accel_bias[2] + '\n')
		self.__accel_bias_file.close()
		print("Accel biases saved successfully!")
		return True
