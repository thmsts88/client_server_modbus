from pymodbus.server.sync import StartSerialServer, StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer,ModbusAsciiFramer
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.version import version
import argparse
from time import sleep, time
from pymodbus.client.sync import ModbusSerialClient,ModbusTcpClient
from custom_log import cust_log
import os

parser = argparse.ArgumentParser()
parser.add_argument('-i','--iface',help='serial interface e.g /dev/ttymxc1',type=str,required=True)
parser.add_argument('-b','--baudrate',help='baudrate e.g. 19200',type=int)
parser.add_argument('-F','--framer',help='server framer',choices='ModbusRtuFramer|ModbusAsciiFramer',type=str)
parser.add_argument('-w','--wait',help='wait time between commands',type=int)
parser.add_argument('-l','--log',help='log filename',type=str)
group=parser.add_mutually_exclusive_group()
group.add_argument('--server', help='act as server',action='store_true')
group.add_argument('--client', help='act as client',action='store_true')
group1=parser.add_mutually_exclusive_group()
group1.add_argument('--rw', help='client read write sequential',action='store_true')
group1.add_argument('--read', help='client read sequential',action='store_true')
group1.add_argument('--rw_multi', help='client read write multiple sequential',action='store_true')
group1.add_argument('--rw_multi_unit', help='client read write multiple unit sequential',action='store_true')
group1.add_argument('--rw_units', help='client read write multiple units',action='store_true')
group2=parser.add_mutually_exclusive_group()
group2.add_argument('--store', help='server store',action='store_true')
group2.add_argument('--slaves', help='server slaves',action='store_true')
group3=parser.add_mutually_exclusive_group()
group3.add_argument('--tcp', help='mode tcp',action='store_true')
group3.add_argument('--serial', help='mode serial',action='store_true')
args = parser.parse_args()

def start_server(iface,baudrate_port,framer):
    IFACE = iface
    STOP_BITS = 1
    BYTE_SIZE = 8
    PARITY ='N'
    BAUD_RATE = baudrate_port
    PORT=BAUD_RATE
    TIMEOUT = 0.001
    if framer == 'ModbusAsciiFramer':
        FRAMER=ModbusAsciiFramer
    else:
        FRAMER=ModbusRtuFramer
    # Define your data store
    if args.store:
        store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [1]*10000),)
        context = ModbusServerContext(slaves=store, single=True)
    if args.slaves:
        slaves  = {
            0x01: ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [1]*10000),),
            0x02: ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [2]*10000),),
            0x03: ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [3]*10000),),
            0x04: ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [4]*10000),),
        }
        context = ModbusServerContext(slaves=slaves, single=False)

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'Pymodbus Test Server'
    identity.ModelName = 'Pymodbus Test Server'
    identity.MajorMinorRevision = version.short()

    def serial():
        log.info('Starting Serial Server...\nInterface '+IFACE
            +'\nFramer '+str(FRAMER)
            +'\nBaudrate '+str(BAUD_RATE))
        
        StartSerialServer(context=context,
                        identity=identity,
                        port=IFACE,
                        framer=FRAMER, 
                        baudrate=BAUD_RATE, 
                        stopbits= STOP_BITS, 
                        bytesize=BYTE_SIZE,
                        parity=PARITY,
                        timeout=TIMEOUT,
                        )

    def tcp(): #not tested
        log.info('Starting TCP Server...\nAddress '+IFACE
                +'\Port '+str(PORT)
                +'\nFramer '+str(FRAMER))
                
        StartTcpServer(context=context, 
                       identity=identity,
                       framer=FRAMER,  
                       address=(IFACE, PORT))

    if args.serial:
        serial()

    if args.tcp:
        tcp()

def start_client(iface,baudrate_port):
    UNIT = 1
    if args.wait:
        WAIT_TIME = args.wait
    else:
        WAIT_TIME = 0
    METHOD = 'rtu'
    if args.framer == 'ModbusAsciiFramer':
        FRAMER=ModbusAsciiFramer
    else:
        FRAMER=ModbusRtuFramer
    IFACE = iface
    STOP_BITS = 1
    BYTE_SIZE = 8
    PARITY ='N'
    BAUD_RATE = baudrate_port
    PORT = BAUD_RATE
    TIMEOUT = 10

    def wait(time):
        log.debug('Wait time between actions: '+str(time))
        sleep(time)
    


    def serial():
        def is_open():
            log.debug('Socket is open: '+ str(client.is_socket_open()))

        log.info('Starting Serial Client...\nMethod '+METHOD
            +'\nInterface '+IFACE
            +'\nBaudrate '+str(BAUD_RATE))
        
        client = ModbusSerialClient(method=METHOD,
                            port=IFACE,
                            stopbits=STOP_BITS,
                            bytesize=BYTE_SIZE,
                            parity=PARITY,
                            baudrate=BAUD_RATE,
                            strict=False,
                            timeout=TIMEOUT,
                            )
        client.connect()        
        is_open()
        wait(WAIT_TIME)

        def read(address,unit,count=1):
            log.info('Holding register..Read\nAddress: '+str(address)
                +'\nUnit: '+str(unit)
                +'\nCount: '+str(count)
                +'\n------------------')
            is_open()
            client.socket.setRTS(False)
            rr = client.read_holding_registers(address=address, count=count, unit=unit)
            log.debug(rr)
            assert(not rr.isError())
            log.info('Address: '+str(address)+':'+str(count-1)
                +'\nUnit: '+str(unit)
                +'\nValue: '+str(rr.registers)
                +'\n------------------') 
        
        def write(address,value,unit,count=1):
            log.info('Holding register...Write\nAddress: '+str(address)
                +'\nValue: '+str(value)
                +'\nUnit: '+str(unit)
                +'\nCount: '+str(count)
                +'\n------------------')
            client.socket.setRTS(True)
            if (count > 1):
                rq = client.write_registers(address=address, values=[value]*count, unit=unit)
                log.debug(rq)
            else:    
                rq = client.write_register(address=address, value=value, unit=unit)
                log.debug(rq)
            assert(not rq.isError())

        def read_write_sequential(unit,max):
            for add in range(max):
                t1=time()
                read(address=add,unit=unit)
                t2=time()
                write(address=add,value=add+10,unit=unit)
                t3=time()
                wait(WAIT_TIME)
                t4=time()
                read(address=add,unit=unit)
                t5=time()
                log.info('Read registers. Time cost '+str(t2-t1)+' second.')
                log.info('Write registers. Time cost '+str(t3-t2-WAIT_TIME)+' second.')
                log.info('Read registers. Time cost '+str(t5-t4)+' second.')
                log.info('R/W/R registers. Time cost '+str(t5-t1-2*WAIT_TIME)+' second.\n------------------')
                wait(WAIT_TIME)

        def read_sequential(unit,max):
            for add in range(max):
                t1=time()
                read(address=add,unit=unit)
                t2=time()
                wait(WAIT_TIME)
                log.info('Read registers. Time cost '+str(t2-t1)+' second.\n------------------')

        def read_multiple(count,value,unit):
            if count > 123:
                log.warning('Maximum register poll count is 125.'
                            +'\nMaximum amount of register written per action is 123.'
                            +'\nCount is set to 123 instead of '+str(count)+'.')
                count=123
            t1=time()
            read(address=0,count=count,unit=unit)
            t2=time()
            write(address=0,value=value,count=count,unit=unit)
            t3=time()
            wait(WAIT_TIME)
            t4=time()
            read(address=0,count=count,unit=unit)
            t5=time()
            log.info('Read registers. Time cost '+str(t2-t1)+' second.')
            log.info('Write registers. Time cost '+str(t3-t2)+' second.')
            log.info('Read registers. Time cost '+str(t5-t4)+' second.')
            log.info('R/W/R registers. Time cost '+str(t5-t1-WAIT_TIME)+' second.\n------------------')
            wait(WAIT_TIME)

        def read_units(count,max,units):
            for i in range(max):
                for unit in range(1,units+1):
                    read_multiple(value=i+1,count=count,unit=unit)

        def read_multiple_sequential(count,max,unit):
            for i in range(max):
                read_multiple(value=i+1,count=count,unit=unit)

        def read_multiple_unit(count,max,units):
            for unit in range(1,units+1):
                read_multiple_sequential(count=count,max=max,unit=unit)

        if args.read:
            read_sequential(unit=UNIT,max=200)
        if args.rw:
            read_write_sequential(unit=UNIT,max=200)
        if args.rw_multi:    
            read_multiple_sequential(count=50,max=50,unit=UNIT)
        if args.rw_multi_unit:
            read_multiple_unit(count=50,max=50,units=4)
        if args.rw_units:
            read_units(count=50,max=50,units=4)

        client.close()

    def tcp():#not tested
        log.info('Starting TCP Client...'
            +'\nAddress '+IFACE
            +'\nPort '+str(PORT))
        client = ModbusTcpClient (host=IFACE, port=PORT, framer=FRAMER)
    

    if args.serial:
        serial()

    if args.tcp:
        tcp()


if args.server:
    log=cust_log('modbus_server'+args.log+'.log')
    start_server(args.iface,args.baudrate,args.framer)

if args.client:
    log=cust_log('modbus_client'+args.log+'.log')
    start_client(args.iface,args.baudrate)