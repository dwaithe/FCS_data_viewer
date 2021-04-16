import struct
import numpy as np
import csv


"""FCS Bulk Correlation Software

    Copyright (C) 2015, 2016  Dominic Waithe

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
import struct


def spc_file_import(file_path):
    f = open(file_path, 'rb')
    macro_time =  float(int(bin(ord(f.read(1)))[2:].rjust(2, '0'),2))*0.1
    
    int(bin(ord(f.read(1)))[2:].rjust(2, '0'),2)
    int(bin(ord(f.read(1)))[2:].rjust(2, '0'),2)
    bin(ord(f.read(1)))[2:].rjust(2, '0')



    overflow = 0
    count1 = 0
    count0 = 0
    chan_arr = []
    true_time_arr = []
    dtime_arr = []
    while True:
        byte = f.read(1)
        if  byte.__len__() ==0 : break
        byte0 = bin(ord(byte))[2:].rjust(8, '0')
        byte1 = bin(ord(f.read(1)))[2:].rjust(8, '0')
        byte2 = bin(ord(f.read(1)))[2:].rjust(8, '0')
        byte3 = bin(ord(f.read(1)))[2:].rjust(8, '0')

        INVALID =  int(byte3[0])
        MTOV = int(byte3[1])
        GAP = int(byte3[2])

        if MTOV == 1: 
            count0 +=1
            overflow += 4096
        if INVALID == 1:
            count1 +=1
        else:
            chan_arr.append(int(byte1[0:4],2))
            true_time_arr.append(int(byte1[4:8]+byte0,2)+overflow)
            dtime_arr.append(4095 - int(byte3[4:8]+byte2,2))
        
            
            #file_out.write(str(int(byte1[4:8]+byte0,2)+overflow)+'\t'+str(4095 - int(byte3[4:8]+byte2,2))+'\t'+str(int(byte1[0:4],2))+'\t'+str(byte3[0:4])+'\n')
    
    return  np.array(chan_arr), np.array(true_time_arr)*(macro_time), np.array(dtime_arr), None


def asc_file_import(file_path):
    f = open(file_path, 'rb')
    count = 0

    out = []
    count = 0
    chan_arr = []
    true_time_arr = []
    dtime_arr = []
    read_header = True
    for line in iter(f.readline, b''):
        count += 1
        if read_header == True:
            if line[0:5] == 'Macro':
                macro_time =  float(line.split(':')[1].split(',')[0])
            if line[0:5] == 'Micro':
                micro_time =  float(line.split(':')[1])
            #print line
            count +=1
            if line[0:18] == 'End of info header':
                read_header = False
                f.readline()#Skips blank line.
                continue
        if read_header == False:
            #Main file reading loop.
            var = line.split(" ")
            
            true_time_arr.append(int(var[0]))
            dtime_arr.append(int(var[1]))
            chan_arr.append(int(var[3]))
        
    
    return  np.array(chan_arr), np.array(true_time_arr)*(macro_time), np.array(dtime_arr), micro_time

def ptuimport(filepath):
    #This import is mostly taken from picoquant resource:
    #https://github.com/PicoQuant/PicoQuant-Time-Tagged-File-Format-Demos/tree/master/PTU/Python

    
    tyEmpty8      = int('FFFF0008', 16);
    tyBool8       = int('00000008', 16);
    tyInt8        = int('10000008', 16);
    tyBitSet64    = int('11000008', 16);
    tyColor8      = int('12000008', 16);
    tyFloat8      = int('20000008', 16);
    tyTDateTime   = int('21000008', 16);
    tyFloat8Array = int('2001FFFF', 16);
    tyAnsiString  = int('4001FFFF', 16);
    tyWideString  = int('4002FFFF', 16);
    tyBinaryBlob  = int('FFFFFFFF', 16);

    rtPicoHarpT3     = int('00010303', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $03 (T3), HW: $03 (PicoHarp)
    rtPicoHarpT2     = int('00010203', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $02 (T2), HW: $03 (PicoHarp)
    rtHydraHarpT3    = int('00010304', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $03 (T3), HW: $04 (HydraHarp)
    rtHydraHarpT2    = int('00010204', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $02 (T2), HW: $04 (HydraHarp)
    rtHydraHarp2T3   = int('01010304', 16);# (SubID = $01 ,RecFmt: $01) (V2), T-Mode: $03 (T3), HW: $04 (HydraHarp)
    rtHydraHarp2T2   = int('01010204', 16);# (SubID = $01 ,RecFmt: $01) (V2), T-Mode: $02 (T2), HW: $04 (HydraHarp)
    rtTimeHarp260NT3 = int('00010305', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $03 (T3), HW: $05 (TimeHarp260N)
    rtTimeHarp260NT2 = int('00010205', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $02 (T2), HW: $05 (TimeHarp260N)
    rtTimeHarp260PT3 = int('00010306', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $03 (T3), HW: $06 (TimeHarp260P)
    rtTimeHarp260PT2 = int('00010206', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $02 (T2), HW: $06 (TimeHarp260P)
    rtMultiHarpNT3   = struct.unpack(">i", bytes.fromhex('00010307'))[0]
    rtMultiHarpNT2   = struct.unpack(">i", bytes.fromhex('00010207'))[0]
    fid = 0
    #TTResultFormat_TTTRRecType =0 ;
    #TTResult_NumberOfRecords = 0; #% Number of TTTR Records in the File;
    #MeasDesc_Resolution =0;      #% Resolution for the Dtime (T3 Only)
    #MeasDesc_GlobalResolution =0;

    
    f = open(filepath, 'rb')
    magic = str(f.read(8))
    if str(magic[2:8]) != "PQTTTR":
        print( 'Your file is an invalid .ptu')

        return False
    version =  f.read(8)
    #print 'version',version

    file_type = {}
    while True:
            #read Tag Head
            TagIdent = f.read(32); # TagHead.Ident
            TagIdent = str.replace(TagIdent.decode(),'\x00','')
            #print 'Tag',TagIdent
            #TagIdent = TagIdent[TagIdent != 0]]#'; # remove #0 and more more readable

            TagIdx =  struct.unpack('i', f.read(4))[0] #TagHead.Idx
            TagTyp =  np.array(struct.unpack('i', f.read(4))[0]).astype(np.uint32) #TagHead.Typ
            #TagHead.Value will be read in the right type function
            #print 'TagIdx',TagIdx
            if TagIdx > -1:
                EvalName = TagIdent+'('+str(TagIdx+1)+')'
            else:
                EvalName = TagIdent

            

            #print('eval',str(EvalName))
            
            
            
            if TagTyp == tyEmpty8:
                struct.unpack('Q', f.read(8))[0]
                #print('empty')
            elif TagTyp ==tyBool8:
                TagInt = struct.unpack('Q', f.read(8))[0]
                if TagInt == 0:
                    #print('False')
                    file_type[EvalName] = False
                else:
                    #print('True')
                    file_type[EvalName] = True
            elif TagTyp == tyInt8:
                TagInt =  struct.unpack('Q', f.read(8))[0]
                file_type[EvalName] = TagInt
                #print('tyInt8',TagInt)
            elif TagTyp == tyBitSet64:
                TagInt = struct.unpack('Q', f.read(8))[0]
                file_type[EvalName] = TagInt
                #print('tyBitSet64',TagInt)
            elif TagTyp == tyColor8:
                TagInt = struct.unpack('Q', f.read(8))[0]
                file_type[EvalName] = TagInt
                #print('tyColor8',TagInt)
            elif TagTyp == tyFloat8:
                TagInt = struct.unpack('d', f.read(8))[0]
                file_type[EvalName] = TagInt
                #print('tyFloat8',TagInt)
            elif TagTyp == tyFloat8Array:
                TagInt = struct.unpack('Q', f.read(8))[0]
                file_type[EvalName] = TagInt
                #print '<Float array with'+str(TagInt / 8)+'Entries>'
                #print('tyFloat8Array',TagInt)
                f.seek(TagInt)
            elif TagTyp == tyTDateTime:
                TagFloat = struct.unpack('d', f.read(8))[0]
                #print('date'+str(TagFloat))
                file_type[EvalName] = TagFloat
            elif TagTyp == tyAnsiString:
                TagInt = int(struct.unpack('Q', f.read(8))[0])
                TagString = f.read(TagInt)
                TagString = str.replace(TagString.decode(),'\x00','')

                #print('tyAnsiString',TagString)
                if TagIdx > -1:
                    EvalName = TagIdent +'{'+str(TagIdx+1)+'}'
                file_type[EvalName] = TagString
            elif TagTyp == tyWideString:
                TagInt = int(struct.unpack('Q', f.read(8))[0])#struct.unpack('i', f.read(4))[0].astype(np.float64)
                TagString = f.read(TagInt)
                TagString = str.replace(TagString.decode(),'\x00','')#struct.unpack('i', f.read(4))[0].astype(np.float64)

                #print('tyWideString',TagString)
                if TagIdx > -1:
                    EvalName = TagIdent +'{'+str(TagIdx+1)+'}'
                file_type[EvalName] = TagString
            elif TagTyp == tyBinaryBlob:
                TagInt = struct.unpack('i', f.read(4))[0].astype(np.float64)
                #print('<Binary Blob with '+str(TagInt)+'Bytes>')
                f.seek(TagInt)
            else:
                print('Illegal Type identifier found! Broken file?',TagTyp)
                
            if TagIdent == "Header_End":
                
                break
    print('\n------------------------\n')
    TTResultFormat_TTTRRecType = file_type['TTResultFormat_TTTRRecType']
    if TTResultFormat_TTTRRecType == rtPicoHarpT3:
        isT2 = False
        print( 'PicoHarp T3 data\n')

    elif TTResultFormat_TTTRRecType == rtPicoHarpT2:
        isT2 =True
        print ('PicoHarp T2 data \n')

    elif TTResultFormat_TTTRRecType == rtHydraHarpT3:
        isT2 = False
        print ('HydraHarp V1 T3 data \n')

    elif TTResultFormat_TTTRRecType == rtHydraHarpT2:
        isT2 = True
        print ('HydraHarp V1 T2 data \n')

    elif TTResultFormat_TTTRRecType == rtHydraHarp2T3:
        isT2 = False
        print ('HydraHarp V2 T3 data \n')

    elif TTResultFormat_TTTRRecType == rtHydraHarp2T2:
        isT2 = True
        print( 'HydraHarp V2 T2 data \n')

    elif TTResultFormat_TTTRRecType == rtTimeHarp260NT3:
        isT2 = False
        print ('TimeHarp260N T3 data \n')

    elif TTResultFormat_TTTRRecType == rtTimeHarp260NT2:
        isT2 = True
        print ('TimeHarp260P T3 data \n')

    elif TTResultFormat_TTTRRecType == rtTimeHarp260PT3:
        isT2 = False
        print ('TimeHarp260P T3 data \n')

    elif TTResultFormat_TTTRRecType == rtTimeHarp260PT2:
        isT2 = True
        print ('TimeHarp260P T2 data \n')
    elif TTResultFormat_TTTRRecType == rtMultiHarpNT3:
        isT2 = False
        print ('rtMultiHarpNT3 T3 data \n')
    elif TTResultFormat_TTTRRecType == rtMultiHarpNT2:
        isT2 = True
        print ('rtMultiHarpNT3 T2 data \n')

    else:
        print('Illegal RecordType')

    #if (isT2):
    #      print '\trecord#\tType\tCh\tTimeTag\tTrueTime/ps\n'
    #else:
    #      print '\trecord#\tType\tCh\tTimeTag\tTrueTime/ns\tDTime\n'

    
    
            
    if TTResultFormat_TTTRRecType   == rtPicoHarpT3: 
        return ReadPT3(f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution'],file_type['MeasDesc_Resolution'])

    elif TTResultFormat_TTTRRecType == rtPicoHarpT2: #ReadPT2
        return readPT2(inputfile,numRecords,MeasDesc_GlobalResolution)
    elif TTResultFormat_TTTRRecType == rtHydraHarpT3: #ReadHT3(1)
        return ReadHT3(1,f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution'],file_type['MeasDesc_Resolution']);
    elif TTResultFormat_TTTRRecType == rtHydraHarpT2: #ReadHT3(1)
        print ('currently this type of file is not supported using this python implementation')
        return False
    elif TTResultFormat_TTTRRecType == rtHydraHarp2T3: 
        return ReadHT3(2,f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution'],file_type['MeasDesc_Resolution']);
    elif TTResultFormat_TTTRRecType == rtHydraHarp2T2: #ReadHT2(2);
        print ('currently this type of file is not supported using this python implementation')
        return False
    elif TTResultFormat_TTTRRecType == rtTimeHarp260NT3: #ReadHT3(2);
        return ReadHT3(2,f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution'],file_type['MeasDesc_Resolution']);
    elif TTResultFormat_TTTRRecType == rtTimeHarp260NT2: #ReadHT2(2);
        print ('currently this type of file is not supported using this python implementation')
        return False
    elif TTResultFormat_TTTRRecType == rtTimeHarp260PT3: #ReadHT3(2);
        return ReadHT3(2,f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution'],file_type['MeasDesc_Resolution']);
    elif TTResultFormat_TTTRRecType == rtTimeHarp260PT2: #ReadHT2(2);
        print ('currently this type of file is not supported using this python implementation')
        return False
    elif TTResultFormat_TTTRRecType == rtMultiHarpNT3: #ReadHT2(2);
        return ReadHT3(2,f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution'],file_type['MeasDesc_Resolution']);
    elif TTResultFormat_TTTRRecType == rtMultiHarpNT2: #ReadHT2(2);
        print ('currently this type of file is not supported using this python implementation')
        return True
    else: 
        print('Illegal RecordType or not yet supported')
        return False
        
    ###Decoder functions
    f.close()
def readPT2(inputfile,numRecords,MeasDesc_GlobalResolution):
    #Contributed by Volodymyr (VolBog).
    chanArr = [0]*TTResult_NumberOfRecords
    trueTimeArr =[0]*TTResult_NumberOfRecords
    dTimeArr= [0]*TTResult_NumberOfRecords
    T2WRAPAROUND = 210698240
    for recNum in range(0, numRecords):
        try:
            recordData = "{0:0{1}b}".format(struct.unpack("<I", inputfile.read(4))[0], 32)
        except:
            print("The file ended earlier than expected, at record %d/%d." \
                  % (recNum, numRecords))
            return False
        channel = int(recordData[0:4], base=2)
        time = int(recordData[4:32], base=2)
        if channel == 0xF:  # Special record
            # lower 4 bits of time are marker bits
            markers = int(recordData[28:32], base=2)
            if markers == 0:  # Not a marker, so overflow
                gotOverflow(1)
                oflcorrection += T2WRAPAROUND
            else:
                # Actually, the lower 4 bits for the time aren't valid because
                # they belong to the marker. But the error caused by them is
                # so small that we can just ignore it.
                truetime = oflcorrection + time
                gotMarker(truetime, markers)
        else:
            if channel > 4:  # Should not occur
                print("Illegal Channel: #%1d %1u" % (recNum, channel))
            truetime = oflcorrection + time
            

            trueTimeArr[cnt_ph] = truetime
            dTimeArr[cnt_ph] = time
            chanArr[cnt_ph] = channel+1
            cnt_ph = cnt_ph +1
    return np.array(chanArr[0:cnt_ph]), np.array(trueTimeArr[0:cnt_ph]), np.array(dTimeArr[0:cnt_ph]), MeasDesc_GlobalResolution* 1e6
# Read HydraHarp/TimeHarp260 T3
def ReadHT3(version,f,TTResult_NumberOfRecords,MeasDesc_GlobalResolution,MeasDesc_Resolution):
    T3WRAPAROUND = 1024
    ofltime = 0
    cnt_Ofl = 0
    cnt_ma = 0
    cnt_ph = 0
    OverflowCorrection = 0
    chanArr = [0]*TTResult_NumberOfRecords
    trueTimeArr =[0]*TTResult_NumberOfRecords
    dTimeArr= [0]*TTResult_NumberOfRecords
    
    for RecNum in range(0,TTResult_NumberOfRecords):
        
       
        #T3Record = struct.unpack('I', f.read(4))[0];
        #nsync = T3Record & 1023
        #truetime = None
        try:
            recordData = "{0:0{1}b}".format(struct.unpack("<I", f.read(4))[0], 32)
        except:
            print("The file ended earlier than expected, at record %d/%d."\
                  % (recNum, TTResult_NumberOfRecords))
            exit(0)

        #dtime = bitand(bitshift(T3Record,-10),32767);
        #dtime = ((T3Record >> 10) & 32767);
        #channel = ((T3Record >> 25) & 63);
        #special = ((T3Record >> 31) & 1);
        special = int(recordData[0:1], base=2)
        channel = int(recordData[1:7], base=2)
        dtime = int(recordData[7:22], base=2)
        nsync = int(recordData[22:32], base=2)
            
        if special == 1:
            if channel  == 63:
                if nsync == 0 or version == 1:
                    OverflowCorrection = OverflowCorrection + T3WRAPAROUND
                    cnt_Ofl = cnt_Ofl+1
                else:
                    OverflowCorrection = OverflowCorrection + T3WRAPAROUND*nsync
                    cnt_Ofl = cnt_Ofl+nsync
            
            if channel >0 and channel < 16:
                true_nSync = OverflowCorrection + nsync
                cnt_ma = cnt_ma +1
        else:
            true_nSync = OverflowCorrection + nsync
            truetime = (true_nSync * MeasDesc_GlobalResolution * 1e9)
            trueTimeArr[cnt_ph] = truetime
            dTimeArr[cnt_ph] = dtime
            chanArr[cnt_ph] = channel+1
            cnt_ph = cnt_ph +1
       
        #PT3
        #dtime = ((T3Record >> 16) & 4095);
        #dtime = bitand(bitshift(T3Record,-16),4095)
    return np.array(chanArr[0:cnt_ph]), np.array(trueTimeArr[0:cnt_ph]), np.array(dTimeArr[0:cnt_ph]), MeasDesc_Resolution* 1e6   

def ReadPT3(f,TTResult_NumberOfRecords,MeasDesc_GlobalResolution,MeasDesc_Resolution):

    cnt_Ofl = 0
    T3WRAPAROUND = 65536
    ofltime = 0
    chanArr = [0]*TTResult_NumberOfRecords
    trueTimeArr =[0]*TTResult_NumberOfRecords
    dTimeArr= [0]*TTResult_NumberOfRecords
    oflcorrection = 0
    cnt_M = 0

    for recNum in range(0,TTResult_NumberOfRecords):
        
        try:
            recordData = "{0:0{1}b}".format(struct.unpack("<I", f.read(4))[0], 32)
        except:
            print("The file ended earlier than expected, at record %d/%d."\
                  % (recNum, TTResult_NumberOfRecords))
            exit(0)
        

        channel = int(recordData[0:4], base=2)
        dtime = int(recordData[4:16], base=2)
        nsync = int(recordData[16:32], base=2)
        
      
        
        
        if channel == 15:
            if dtime == 0: # Not a marker, so overflow
                #  dgotOverflow(1)
                oflcorrection += T3WRAPAROUND
            else:
                truensync = oflcorrection + nsync
                #gotMarker(truensync, dtime)
                
            
        else:
            if channel == 0 and channel > 4:
                pass
            truensync = oflcorrection + nsync;    
            truetime = (truensync * MeasDesc_GlobalResolution * 1e9)
            trueTimeArr[cnt_M] = truetime
            dTimeArr[cnt_M] = dtime
            chanArr[cnt_M] = channel
            cnt_M += 1
                #f1.write("MA:%1u "+markers+" ")
        
        

    return np.array(chanArr)[0:cnt_M], np.array(trueTimeArr)[0:cnt_M], np.array(dTimeArr)[0:cnt_M], MeasDesc_Resolution* 1e9
def csvimport(filepath):
    """Function for importing time-tag data directly into FCS point software. """
    r_obj = csv.reader(open(filepath, 'r'))
    line_one = next(r_obj)
    if line_one.__len__()>1:
        if float(line_one[1]) == 2:
            
            version = 2
        else:
            print ('version not known:',line_one[1])
    
    if version == 2:
        type =str(next(r_obj)[1])
        
        if type == "pt uncorrelated":
            Resolution = float(r_obj.next()[1])
            chanArr = []
            trueTimeArr = []
            dTimeArr = []
            line = r_obj.next()
            while  line[0] != 'end':

                chanArr.append(int(line[0]))
                trueTimeArr.append(float(line[1]))
                dTimeArr.append(int(line[2]))
                line = r_obj.next()
            return np.array(chanArr), np.array(trueTimeArr), np.array(dTimeArr), Resolution
        else:
            print ('type not recognised')
            return None, None,None,None

    

def pt3import(filepath):
    """The file import for the .pt3 file"""
    f = open(filepath, 'rb')
    Ident = f.read(16)
    FormatVersion = f.read(6)
    CreatorName = f.read(18)
    CreatorVersion = f.read(12)
    FileTime = f.read(18)
    CRLF = f.read(2)
    CommentField = f.read(256)
    Curves = struct.unpack('i', f.read(4))[0]
    BitsPerRecord = struct.unpack('i', f.read(4))[0]
    RoutingChannels = struct.unpack('i', f.read(4))[0]
    NumberOfBoards = struct.unpack('i', f.read(4))[0]
    ActiveCurve = struct.unpack('i', f.read(4))[0]
    MeasurementMode = struct.unpack('i', f.read(4))[0]
    SubMode = struct.unpack('i', f.read(4))[0]
    RangeNo = struct.unpack('i', f.read(4))[0]
    Offset = struct.unpack('i', f.read(4))[0]
    AcquisitionTime = struct.unpack('i', f.read(4))[0]
    StopAt = struct.unpack('i', f.read(4))[0]
    StopOnOvfl = struct.unpack('i', f.read(4))[0]
    Restart = struct.unpack('i', f.read(4))[0]
    DispLinLog = struct.unpack('i', f.read(4))[0]
    DispTimeFrom = struct.unpack('i', f.read(4))[0]
    DispTimeTo = struct.unpack('i', f.read(4))[0]
    DispCountFrom = struct.unpack('i', f.read(4))[0]
    DispCountTo = struct.unpack('i', f.read(4))[0]
    DispCurveMapTo = [];
    DispCurveShow =[];
    for i in range(0,8):
        DispCurveMapTo.append(struct.unpack('i', f.read(4))[0]);
        DispCurveShow.append(struct.unpack('i', f.read(4))[0]);
    ParamStart =[];
    ParamStep =[];
    ParamEnd =[];
    for i in range(0,3):
        ParamStart.append(struct.unpack('i', f.read(4))[0]);
        ParamStep.append(struct.unpack('i', f.read(4))[0]);
        ParamEnd.append(struct.unpack('i', f.read(4))[0]);
        
    RepeatMode = struct.unpack('i', f.read(4))[0]
    RepeatsPerCurve = struct.unpack('i', f.read(4))[0]
    RepeatTime = struct.unpack('i', f.read(4))[0]
    RepeatWait = struct.unpack('i', f.read(4))[0]
    ScriptName = f.read(20)

    #The next is a board specific header

    HardwareIdent = f.read(16)
    HardwareVersion = f.read(8)
    HardwareSerial = struct.unpack('i', f.read(4))[0]
    SyncDivider = struct.unpack('i', f.read(4))[0]

    CFDZeroCross0 = struct.unpack('i', f.read(4))[0]
    CFDLevel0 = struct.unpack('i', f.read(4))[0]
    CFDZeroCross1 = struct.unpack('i', f.read(4))[0]
    CFDLevel1 = struct.unpack('i', f.read(4))[0]

    Resolution = struct.unpack('f', f.read(4))[0]

    #below is new in format version 2.0

    RouterModelCode      = struct.unpack('i', f.read(4))[0]
    RouterEnabled        = struct.unpack('i', f.read(4))[0]

    #Router Ch1
    RtChan1_InputType    = struct.unpack('i', f.read(4))[0]
    RtChan1_InputLevel   = struct.unpack('i', f.read(4))[0]
    RtChan1_InputEdge    = struct.unpack('i', f.read(4))[0]
    RtChan1_CFDPresent   = struct.unpack('i', f.read(4))[0]
    RtChan1_CFDLevel     = struct.unpack('i', f.read(4))[0]
    RtChan1_CFDZeroCross = struct.unpack('i', f.read(4))[0]
    #Router Ch2
    RtChan2_InputType    = struct.unpack('i', f.read(4))[0]
    RtChan2_InputLevel   = struct.unpack('i', f.read(4))[0]
    RtChan2_InputEdge    = struct.unpack('i', f.read(4))[0]
    RtChan2_CFDPresent   = struct.unpack('i', f.read(4))[0]
    RtChan2_CFDLevel     = struct.unpack('i', f.read(4))[0]
    RtChan2_CFDZeroCross = struct.unpack('i', f.read(4))[0]
    #Router Ch3
    RtChan3_InputType    = struct.unpack('i', f.read(4))[0]
    RtChan3_InputLevel   = struct.unpack('i', f.read(4))[0]
    RtChan3_InputEdge    = struct.unpack('i', f.read(4))[0]
    RtChan3_CFDPresent   = struct.unpack('i', f.read(4))[0]
    RtChan3_CFDLevel     = struct.unpack('i', f.read(4))[0]
    RtChan3_CFDZeroCross = struct.unpack('i', f.read(4))[0]
    #Router Ch4
    RtChan4_InputType    = struct.unpack('i', f.read(4))[0]
    RtChan4_InputLevel   = struct.unpack('i', f.read(4))[0]
    RtChan4_InputEdge    = struct.unpack('i', f.read(4))[0]
    RtChan4_CFDPresent   = struct.unpack('i', f.read(4))[0]
    RtChan4_CFDLevel     = struct.unpack('i', f.read(4))[0]
    RtChan4_CFDZeroCross = struct.unpack('i', f.read(4))[0]

    #The next is a T3 mode specific header.
    ExtDevices = struct.unpack('i', f.read(4))[0]

    Reserved1 = struct.unpack('i', f.read(4))[0]
    Reserved2 = struct.unpack('i', f.read(4))[0]
    CntRate0 = struct.unpack('i', f.read(4))[0]
    CntRate1 = struct.unpack('i', f.read(4))[0]

    StopAfter = struct.unpack('i', f.read(4))[0]
    StopReason = struct.unpack('i', f.read(4))[0]
    Records = struct.unpack('i', f.read(4))[0]
    ImgHdrSize =struct.unpack('i', f.read(4))[0]

    #Special Header for imaging.
    if ImgHdrSize > 0:
        ImgHdr = struct.unpack('i', f.read(ImgHdrSize))[0]
    ofltime = 0;

    cnt_1=0; cnt_2=0; cnt_3=0; cnt_4=0; cnt_Ofl=0; cnt_M=0; cnt_Err=0; # just counters
    WRAPAROUND=65536;

    #Put file Save info here.

    syncperiod = 1e9/CntRate0;
    #outfile stuff here.
    #fpout.
    #T3RecordArr = [];
    
    chanArr = [0]*Records
    trueTimeArr =[0]*Records
    dTimeArr=[0]*Records
    #f1=open('./testfile', 'w+')
    for b in range(0,Records):
        T3Record = struct.unpack('I', f.read(4))[0];
        
        #T3RecordArr.append(T3Record)
        nsync = T3Record & 65535
        chan = ((T3Record >> 28) & 15);
        chanArr[b]=chan
        #f1.write(str(i)+" "+str(T3Record)+" "+str(nsync)+" "+str(chan)+" ")
        dtime = 0;
        
        if chan == 1:
            cnt_1 = cnt_1+1;dtime = ((T3Record >> 16) & 4095);#f1.write(str(dtime)+" ")
        elif chan == 2: 
            cnt_2 = cnt_2+1;dtime = ((T3Record >> 16) & 4095);#f1.write(str(dtime)+" ")
        elif chan == 3: 
            cnt_3 = cnt_3+1;dtime = ((T3Record >> 16) & 4095);#f1.write(str(dtime)+" ")
        elif chan == 4: 
            cnt_4 = cnt_4+1;dtime = ((T3Record >> 16) & 4095);#f1.write(str(dtime)+" ")
        elif chan == 15:
            markers = ((T3Record >> 16) & 15);
            
            if markers ==0:
                ofltime = ofltime +WRAPAROUND;
                cnt_Ofl = cnt_Ofl+1
                #f1.write("Ofl "+" ")
            else:
                cnt_M=cnt_M+1
                #f1.write("MA:%1u "+markers+" ")
            
        truensync = ofltime + nsync;
        truetime = (truensync * syncperiod) + (dtime*Resolution);
        trueTimeArr[b] = truetime
        dTimeArr[b] = dtime
        
        #f1.write(str(truensync)+" "+str(truetime)+"\n")
    f.close();
    #f1.close();
    

    
    return np.array(chanArr), np.array(trueTimeArr), np.array(dTimeArr), Resolution
def pt2import(filepath):
    """The file import for the .pt3 file"""
    f = open(filepath, 'rb')
    Ident = f.read(16)
    FormatVersion = f.read(6)
    CreatorName = f.read(18)
    CreatorVersion = f.read(12)
    FileTime = f.read(18)
    CRLF = f.read(2)
    CommentField = f.read(256)
    Curves = struct.unpack('i', f.read(4))[0]
    BitsPerRecord = struct.unpack('i', f.read(4))[0]

    RoutingChannels = struct.unpack('i', f.read(4))[0]
    NumberOfBoards = struct.unpack('i', f.read(4))[0]
    ActiveCurve = struct.unpack('i', f.read(4))[0]
    MeasurementMode = struct.unpack('i', f.read(4))[0]
    SubMode = struct.unpack('i', f.read(4))[0]
    RangeNo = struct.unpack('i', f.read(4))[0]
    Offset = struct.unpack('i', f.read(4))[0]
    AcquisitionTime = struct.unpack('i', f.read(4))[0]
    StopAt = struct.unpack('i', f.read(4))[0]
    StopOnOvfl = struct.unpack('i', f.read(4))[0]
    Restart = struct.unpack('i', f.read(4))[0]
    DispLinLog = struct.unpack('i', f.read(4))[0]
    DispTimeFrom = struct.unpack('i', f.read(4))[0]
    DispTimeTo = struct.unpack('i', f.read(4))[0]
    DispCountFrom = struct.unpack('i', f.read(4))[0]
    DispCountTo = struct.unpack('i', f.read(4))[0]

    DispCurveMapTo = [];
    DispCurveShow =[];
    for i in range(0,8):
        DispCurveMapTo.append(struct.unpack('i', f.read(4))[0]);
        DispCurveShow.append(struct.unpack('i', f.read(4))[0]);
    ParamStart =[];
    ParamStep =[];
    ParamEnd =[];
    for i in range(0,3):
        ParamStart.append(struct.unpack('i', f.read(4))[0]);
        ParamStep.append(struct.unpack('i', f.read(4))[0]);
        ParamEnd.append(struct.unpack('i', f.read(4))[0]);
        
    RepeatMode = struct.unpack('i', f.read(4))[0]
    RepeatsPerCurve = struct.unpack('i', f.read(4))[0]
    RepeatTime = struct.unpack('i', f.read(4))[0]
    RepeatWait = struct.unpack('i', f.read(4))[0]
    ScriptName = f.read(20)

    #The next is a board specific header

    HardwareIdent = f.read(16)
    HardwareVersion = f.read(8)
    HardwareSerial = struct.unpack('i', f.read(4))[0]
    SyncDivider = struct.unpack('i', f.read(4))[0]

    CFDZeroCross0 = struct.unpack('i', f.read(4))[0]
    CFDLevel0 = struct.unpack('i', f.read(4))[0]
    CFDZeroCross1 = struct.unpack('i', f.read(4))[0]
    CFDLevel1 = struct.unpack('i', f.read(4))[0]

    Resolution = struct.unpack('f', f.read(4))[0]

    #below is new in format version 2.0

    RouterModelCode      = struct.unpack('i', f.read(4))[0]
    RouterEnabled        = struct.unpack('i', f.read(4))[0]

    #Router Ch1
    RtChan1_InputType    = struct.unpack('i', f.read(4))[0]
    RtChan1_InputLevel   = struct.unpack('i', f.read(4))[0]
    RtChan1_InputEdge    = struct.unpack('i', f.read(4))[0]
    RtChan1_CFDPresent   = struct.unpack('i', f.read(4))[0]
    RtChan1_CFDLevel     = struct.unpack('i', f.read(4))[0]
    RtChan1_CFDZeroCross = struct.unpack('i', f.read(4))[0]
    #Router Ch2
    RtChan2_InputType    = struct.unpack('i', f.read(4))[0]
    RtChan2_InputLevel   = struct.unpack('i', f.read(4))[0]
    RtChan2_InputEdge    = struct.unpack('i', f.read(4))[0]
    RtChan2_CFDPresent   = struct.unpack('i', f.read(4))[0]
    RtChan2_CFDLevel     = struct.unpack('i', f.read(4))[0]
    RtChan2_CFDZeroCross = struct.unpack('i', f.read(4))[0]
    #Router Ch3
    RtChan3_InputType    = struct.unpack('i', f.read(4))[0]
    RtChan3_InputLevel   = struct.unpack('i', f.read(4))[0]
    RtChan3_InputEdge    = struct.unpack('i', f.read(4))[0]
    RtChan3_CFDPresent   = struct.unpack('i', f.read(4))[0]
    RtChan3_CFDLevel     = struct.unpack('i', f.read(4))[0]
    RtChan3_CFDZeroCross = struct.unpack('i', f.read(4))[0]
    #Router Ch4
    RtChan4_InputType    = struct.unpack('i', f.read(4))[0]
    RtChan4_InputLevel   = struct.unpack('i', f.read(4))[0]
    RtChan4_InputEdge    = struct.unpack('i', f.read(4))[0]
    RtChan4_CFDPresent   = struct.unpack('i', f.read(4))[0]
    RtChan4_CFDLevel     = struct.unpack('i', f.read(4))[0]
    RtChan4_CFDZeroCross = struct.unpack('i', f.read(4))[0]

    #The next is a T3 mode specific header.
    ExtDevices = struct.unpack('i', f.read(4))[0]

    Reserved1 = struct.unpack('i', f.read(4))[0]
    Reserved2 = struct.unpack('i', f.read(4))[0]
    CntRate0 = struct.unpack('i', f.read(4))[0]
    CntRate1 = struct.unpack('i', f.read(4))[0]

    StopAfter = struct.unpack('i', f.read(4))[0]
    StopReason = struct.unpack('i', f.read(4))[0]
    Records = struct.unpack('i', f.read(4))[0]
    ImgHdrSize =struct.unpack('i', f.read(4))[0]

    #Special Header for imaging.
    if ImgHdrSize > 0:
        ImgHdr = struct.unpack('i', f.read(ImgHdrSize))[0]


    ofltime = 0;

    cnt_0=0; cnt_1=0; cnt_2=0; cnt_3=0;cnt_4=0; cnt_Ofl=0; cnt_M=0; cnt_Err=0; # just counters
    RESOL=4E-12;   # 4ps
    WRAPAROUND=210698240;
    chanArr = [0]*Records
    trueTimeArr =[0]*Records
    dTimeArr=[0]*Records
    
    for b in range(0,Records):
        T2Record = struct.unpack('i', f.read(4))[0]
        T2time = T2Record & 268435455
        chan = ((T2Record >> 28) & 15);
        chanArr[b]=chan

        if chan ==0:
            cnt_0 = cnt_0+1;
        elif chan == 1:
            cnt_1 = cnt_1+1;
        elif chan == 2: 
            cnt_2 = cnt_2+1;
        elif chan == 3: 
            cnt_3 = cnt_3+1;
        elif chan == 4: 
            cnt_4 = cnt_4+1;
        elif chan == 15:
            markers = T2Record & 15;
            
            if markers ==0:
                ofltime = ofltime +WRAPAROUND;
                cnt_Ofl = cnt_Ofl+1
                
            else:
                cnt_M=cnt_M+1
                
        else:
            cnt_Err = cnt_Err+1
        time = T2time + ofltime;
        trueTimeArr[b] = time*RESOL

    



    return np.array(chanArr)+1, np.array(trueTimeArr)*1000000000, np.array(dTimeArr), Resolution
