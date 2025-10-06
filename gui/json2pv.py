############################# load the json file to contains all PVs
import json

def load_pv_json(file_path='../ioc/All_PV.json'):

  with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)


  temp_DIG_BOARD_PV = []
  temp_DIG_CHANNEL_PV = []

  temp_MTRG_BOARD_PV = []
  temp_RTRG_BOARD_PV = []

  temp_DAQ_PV = []

  count = 0

  for item in data:

    # print("----Processing item:", item[0])
    subField = item[1]

    if "MDIG" in item[0] or "SDIG" in item[0]:

      isChannel = False
      if "led_green_state" in item[0]:
        pvFirst = item[0].split(":")[:-1]
        pv = pvFirst[0]+ ":" + pvFirst[1] + ":led_green_state"
        isChannel = True
      
      elif "led_red_state" in item[0]:
        pvFirst = item[0].split(":")[:-1]
        pv = pvFirst[0]+ ":" + pvFirst[1] + ":led_red_state"
        isChannel = True

      elif item[0][-1].isdigit():
        pv = item[0][:-1]
        isChannel = True
      
      elif item[0].endswith("RBV"):
        pv = item[0][:-4]
        if pv[-1].isdigit():
          pv = pv[:-1]
          isChannel = True
        else:
          # print( f"Board PV {count}: {item[0]} | {pv}" )
          count += 1
          isChannel = False

      elif item[0].endswith("LONGOUT"):
        pv = item[0][:-7]
        if pv[-1].isdigit():
          pv = pv[:-1]
          isChannel = True
        else:
          # print( f"Board PV {count}: {item[0]} | {pv}" )
          count += 1
          isChannel = False

      elif item[0].endswith("LONGIN"):
        pv = item[0][:-6]
        if pv[-1].isdigit():
          pv = pv[:-1]
          isChannel = True
        else:
          # print( f"Board PV {count}: {item[0]} | {pv}" )
          count += 1
          isChannel = False

      else:
        pv = item[0]
        # print( f"Board PV {count}: {item[0]} | {pv}" )
        count += 1
        isChannel = False


      # print("----Processing PV:", item[0], "isChannel=", isChannel)

      if isChannel:

        # Sort temp_DIG_CHANNEL_PV so that entries with 'RBV' in subField are at the front
        temp_DIG_CHANNEL_PV.sort(key=lambda x: 'RBV' not in x[1])

        if pv not in [x[0] for x in temp_DIG_CHANNEL_PV]:
          pv = (pv, subField) 
          temp_DIG_CHANNEL_PV.append(pv)

      else:

        temp_DIG_BOARD_PV.sort(key=lambda x: 'RBV' not in x[1])

        if pv not in [x[0] for x in temp_DIG_BOARD_PV]:
          pv = (pv, subField)
          temp_DIG_BOARD_PV.append(pv)


    elif "MTRG" in item[0]:

      if item[0].endswith("RBV"):
        pv = item[0][:-4]
      elif item[0].endswith("LONGOUT"):
        pv = item[0][:-7]
      elif item[0].endswith("LONGIN"):
        pv = item[0][:-6]
      else:
        pv = item[0]

      pv = (pv, subField)

      temp_MTRG_BOARD_PV.append(pv)

    elif "RTR" in item[0]:

      if item[0].endswith("RBV"):
        pv = item[0][:-4]
      elif item[0].endswith("LONGOUT"):
        pv = item[0][:-7]
      elif item[0].endswith("LONGIN"):
        pv = item[0][:-6]
      else:
        pv = item[0]

      pv = (pv, subField)

      temp_RTRG_BOARD_PV.append(pv)

    elif "DAQ" in item[0]:

      temp_DAQ_PV.append( item )
    
  # print("##########################################################################")
  # for i,  pv in enumerate(temp_DIG_CHANNEL_PV):
  #   print(f"{i:03d} | {pv[0]:40s} | {pv[1]}")
  
  # for i,  pv in enumerate(temp_DIG_BOARD_PV):
  #   print(f"{i:03d} | {pv[0]:50s} | {pv[1]}")
  
  # for i,  pv in enumerate(temp_RTRG_BOARD_PV):
  #   print(f"{i:03d} | {pv[0]:50s} | {pv[1]}")

  # for i,  pv in enumerate(temp_MTRG_BOARD_PV):
  #   print(f"{i:03d} | {pv[0]:50s} | {pv[1]}")

  # for i,  pv in enumerate(temp_DAQ_PV):
  #   print(f"{i:03d} | {pv[0]:50s} | {pv[1]}")
  print("##########################################################################")

  return temp_DIG_CHANNEL_PV, temp_DIG_BOARD_PV, temp_RTRG_BOARD_PV, temp_MTRG_BOARD_PV, temp_DAQ_PV  


#========================== check the pv[1] and reformate if needed
from class_PV import PV
import epics


def FormatPVList(temp_PV_list):

  epics.ca.clear_cache()

  PV_list = []
  Board_list = []

  for i, pv in enumerate(temp_PV_list):
    if ":" in pv[0]:

      pvName = pv[0].split(":")[-1]
      bdName = ":".join(pv[0].split(":")[:-1])

      if bdName not in Board_list:
        Board_list.append(bdName)

    else:

      pvName = pv[0]
      bdName = ""


    # if pvName != "reg_MISC_STAT"  and pvName != "reg_MISC_STAT_REG":
    #   if pvName.startswith("reg_") or pvName.startswith("regin_"):
    #     continue

    mtrg_skip_pv = ["reg_TRIG_RAM_", "reg_VETO_RAM_", "reg_SWEEP_RAM_"]
    if any(pvName.startswith(prefix) for prefix in mtrg_skip_pv):
      continue

    PV_obj = PV()
    PV_obj.SetName(pvName)

    if pvName == "reg_FIFO_RESETS" :
      PV_obj.AddState("0")
      PV_obj.AddState("1")

    field_names = [x for x in pv[1]]
    field_value = [pv[1][x] for x in pv[1]]

    states = []

    for fn, fv in zip(field_names, field_value):
      if fn.endswith("NAM") or fn.endswith("ST"):
        PV_obj.AddState(fv)

    if "RBV" in pv[1] and pv[1]['RBV'] == "ONLY":
      PV_obj.SetRBVExist(True)
      PV_obj.SetReadONLY(True)
    else:
      PV_obj.SetReadONLY(False)

    if "RBV" in pv[1] and pv[1]['RBV'] == "Exist":
      PV_obj.SetRBVExist(True)
      PV_obj.SetReadONLY(False)

    PV_list.append(PV_obj)

        
  return PV_list, Board_list

#========================== Finally generate the PV lists
def GeneratePVLists(file_path='../ioc/All_PV.json'):
  temp_DIG_CHANNEL_PV, temp_DIG_BOARD_PV, temp_RTRG_BOARD_PV, temp_MTRG_BOARD_PV, temp_DAQ_PV = load_pv_json(file_path)

  DIG_CHANNEL_PV, _ = FormatPVList(temp_DIG_CHANNEL_PV)
  DIG_BOARD_PV, DIG_BOARD_LIST = FormatPVList(temp_DIG_BOARD_PV)

  RTR_BOARD_PV, RTR_BOARD_LIST = FormatPVList(temp_RTRG_BOARD_PV)
  MTRG_BOARD_PV, MTRG_BOARD_LIST = FormatPVList(temp_MTRG_BOARD_PV)

  DAQ_PV, _ = FormatPVList(temp_DAQ_PV)

  #------ sort PV_list based on the PV name
  DIG_CHANNEL_PV.sort(key=lambda pv: pv.name)
  DIG_BOARD_PV.sort(key=lambda pv: pv.name)
  RTR_BOARD_PV.sort(key=lambda pv: pv.name)
  MTRG_BOARD_PV.sort(key=lambda pv: pv.name)
  DAQ_PV.sort(key=lambda pv: pv.name)

  # for i,  pv in enumerate(DIG_CHANNEL_PV):
  #   print(f"{i:03d} | {pv}")

  # for i,  pv in enumerate(DIG_BOARD_PV):
  #   print(f"{i:03d} | {pv}")

  # for i,  pv in enumerate(RTR_BOARD_PV):
  #   print(f"{i:03d} | {pv}")

  # skip_pv = ["VETO_RAM", "TRIG_RAM", "SWEEP_RAM"]

  # count = 0
  # for i,  pv in enumerate(MTRG_BOARD_PV):
  #   pvName = pv.name.split(":")[-1]
  #   if any(pvName.startswith(prefix) for prefix in skip_pv):
  #     continue
  #   print(f"{i:03d} | {count:03d} | {pv}")
  #   count += 1


  for i,  pv in enumerate(DAQ_PV):
    print(f"{i:03d} | {pv}")


  # print("##########################################################################")

  return DIG_CHANNEL_PV, DIG_BOARD_PV, RTR_BOARD_PV, MTRG_BOARD_PV, DIG_BOARD_LIST, RTR_BOARD_LIST, MTRG_BOARD_LIST, DAQ_PV




