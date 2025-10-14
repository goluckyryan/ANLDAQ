from class_PV import PV
from class_Board import Board

class LinkSys:
  def __init__(self, MTRG : Board, RTR_list, DIG_list):
    self.MTRG_boardName = MTRG.BD_name
    self.RTR_boardName_list = []
    for rtr in RTR_list:
      self.RTR_boardName_list.append(rtr.BD_name)

    self.DIG_boardName_list = []
    for dig in DIG_list:
      self.DIG_boardName_list.append(dig.BD_name)

  def Set_MTRG_LINK_MAP(self, link_map):
    self.MTRG_LinkMap = link_map

    # the link map take the form 
    # map = [ ["A", "RTR1", Propagate_Flag], ["B", "RTR2", Propagate_Flag], ... ]

  def Set_RTR_LINK_MAP(self, link_map):
    self.RTR_LinkMap = link_map

    # the link map take the form 
    # map = [ 
    #   ["A", "B", "C", "X", "X", ... ], # RTR1 link map
    #   ["A", "X", ...],  # RTR2 link map
    #   ... 
    #]


  def SetPVManually(self, board_name, pv_name, value):
    pv = PV()
    pv.SetName(f"{board_name}:{pv_name}")
    pv.SetValue(value, debug=False)

  #^>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
  def Stage1_Setup(self, mtrg_clk_src="local"):
    print(">>>>>>>>>>>>>>>>>>>>> Stage 1 setup: Initialize Master Trigger to send SYNC and clock to all Routers")

    print("################ 1A: setting master to local clock")
    if mtrg_clk_src == "local":
      mtrg_clk_src = 0
    else:
      mtrg_clk_src = 1

    pvValList = [
      ["ClkSrc", mtrg_clk_src],   # 0=local, 1=external
      ["LINK_L_PROPAGATE_F1", mtrg_clk_src],
      ["LINK_L_PROPAGATE_F3", 0],
      ["LINK_L_PROPAGATE_F4", 0],
      ["LINK_L_PROPAGATE_F5", 0],
      ["LINK_L_PROPAGATE_F6", 0],
      ["LINK_L_PROPAGATE_F7", 0],
      ["LINK_R_PROPAGATE_F3", 0],
      ["LINK_R_PROPAGATE_F4", 0],
      ["LINK_R_PROPAGATE_F5", 0],
      ["LINK_R_PROPAGATE_F6", 0],
      ["LINK_R_PROPAGATE_F7", 0],
      ["LINK_U_PROPAGATE_F3", 0],
      ["LINK_U_PROPAGATE_F4", 0],
      ["LINK_U_PROPAGATE_F5", 0],
      ["LINK_U_PROPAGATE_F6", 0],
      ["LINK_U_PROPAGATE_F7", 0],
      ["reg_STARTING_TIMESTAMP_HI", 0],
      ["reg_STARTING_TIMESTAMP_MID", 0],
      ["reg_STARTING_TIMESTAMP_LOW", 0]
    ]
    for pv_name, value in pvValList:
      self.SetPVManually(self.MTRG_boardName, pv_name, value)

    # Assert reset and then release it after setting other control bits.
    print("################ 1B: clear any leftover states in link-init of master trigger")

    pv_settings = [
        ("RESET_LINK_INIT", 1),
        ("LOCK_RETRY", 0),
        ("LOCK_ACK", 0),
        ("LINK_L_STRINGENT", 0),
        ("LINK_R_STRINGENT", 0),
        ("LINK_U_STRINGENT", 0),
        ("IMP_SYNC", 0)
    ]
    for pv_name, value in pv_settings:
        self.SetPVManually(self.MTRG_boardName, pv_name, value)

    # In readiness for later, clear all trigger mask bits to turn off all triggers
    print("################ 1C: Resetting trigger configuration to all disabled")

    trigger_settings = [
        ("EN_MAN_AUX", 0),
        ("EN_SUM_X", 0),
        ("EN_SUM_Y", 0),
        ("EN_SUM_XY", 0),
        ("EN_ALGO5", 0),
        ("EN_LINK_L", 0),
        ("EN_LINK_R", 0),
        ("EN_MYRIAD_LINK_U", 0)
    ]
    for pv_name, value in trigger_settings:
        self.SetPVManually(self.MTRG_boardName, pv_name, value)

    # Ensure that all masking for coincidence trigger (Algo 5) is OFF
    coinc_mask_settings = [
        ("reg_COINC_TRIG_MASK", 0),
        ("COINC_TRIG_MASK_A1", 0),
        ("COINC_TRIG_MASK_A2", 0),
        ("COINC_TRIG_MASK_A3", 0),
        ("COINC_TRIG_MASK_A4", 0),
        ("COINC_TRIG_MASK_A6", 0),
        ("COINC_TRIG_MASK_A7", 0),
        ("COINC_TRIG_MASK_B1", 0),
        ("COINC_TRIG_MASK_B2", 0),
        ("COINC_TRIG_MASK_B3", 0),
        ("COINC_TRIG_MASK_B4", 0),
        ("COINC_TRIG_MASK_B6", 0),
        ("COINC_TRIG_MASK_B7", 0)
    ]
    for pv_name, value in coinc_mask_settings:
        self.SetPVManually(self.MTRG_boardName, pv_name, value)

    # Set trigger algorithm 5 to coincidence trigger
    self.SetPVManually(self.MTRG_boardName, "ALGO_5_SELECT", 1)

    # Selections of mode for algorithms 6,7,8 (potential remote triggers)
    algo_mode_settings = [
        ("LINK_L_IS_TRIGGER_TYPE", 0),
        ("LINK_R_IS_TRIGGER_TYPE", 0),
        ("LINK_U_IS_TRIGGER_TYPE", 1)
    ]
    for pv_name, value in algo_mode_settings:
        self.SetPVManually(self.MTRG_boardName, pv_name, value)

    print("################ 1D: Clearing all per-algorithm enables of trigger veto")

    veto_Name = [
       ["EN_NIM_VETO_A", 0],
       ["EN_NIM_VETO_B", 0],
       ["EN_NIM_VETO_C", 0],
       ["EN_NIM_VETO_D", 0],
       ["EN_NIM_VETO_E", 0],
       ["EN_NIM_VETO_F", 0],
       ["EN_NIM_VETO_G", 0],
       ["EN_NIM_VETO_H", 0],
       ["EN_RAM_VETO_A", 0],
       ["EN_RAM_VETO_B", 0],
       ["EN_RAM_VETO_C", 0],
       ["EN_RAM_VETO_D", 0],
       ["EN_RAM_VETO_E", 0],
       ["EN_RAM_VETO_F", 0],
       ["EN_RAM_VETO_G", 0],
       ["EN_RAM_VETO_H", 0],
       ["EN_THROTTLE_VETO_A", 0],
       ["EN_THROTTLE_VETO_B", 0],
       ["EN_THROTTLE_VETO_C", 0],
       ["EN_THROTTLE_VETO_D", 0],
       ["EN_THROTTLE_VETO_E", 0],
       ["EN_THROTTLE_VETO_F", 0],
       ["EN_THROTTLE_VETO_G", 0],
       ["EN_THROTTLE_VETO_H", 0]
    ]
    for pv_name, value in veto_Name:
      self.SetPVManually(self.MTRG_boardName, pv_name, value)

    print("################ 1E: Clearing all global enables of trigger veto")

    global_veto_settings = [
        ["SOFTWARE_VETO",      0],
        ["EN_RAM_VETO",        0],
        ["ENBL_MON7_VETO",     0],
        ["ENBL_NIM_VETO",      0],
        ["ENBL_THROTTLE_VETO", 0]
    ]
    for pv_name, value in global_veto_settings:
        self.SetPVManually(self.MTRG_boardName, pv_name, value)

    print("################ 1F: setting master links L,R,U DEN/REN/SYNC all on")

    lru_ctl_settings = [
        ["LRUCtl00", 1],  # link L DEN
        ["LRUCtl01", 1],  # link L REN
        ["LRUCtl02", 1],  # link L Sync
        ["LRUCtl04", 1],  # link R DEN
        ["LRUCtl05", 1],  # link R REN
        ["LRUCtl06", 1],  # link R Sync
        ["LRUCtl08", 1],  # link U DEN
        ["LRUCtl09", 1],  # link U REN
        ["LRUCtl10", 1],  # link U Sync
        ["EN_RTR_DCBAL", 1]  # Enable DC Balance on master trigger
    ]
    for pv_name, value in lru_ctl_settings:
        self.SetPVManually(self.MTRG_boardName, pv_name, value)

    print("################ 1G: Setting master trigger Input Link Mask")

    for MT_LINK in self.MTRG_LinkMap:
      link_id = MT_LINK[0]
      link_name = MT_LINK[1]
      Propagate = MT_LINK[2]
      print(f"Master Trigger link {link_id} is {link_name:>6s}. Propagate = {Propagate}")
      if link_name == "MASKED":
        (ILM, XLM, YLM) = (1, 1, 1)
      elif link_name in ["PIXIE", "DFMA", "DUB", "DXA"]: 
        (ILM, XLM, YLM) = (0, 1, 1)
      else:
        (ILM, XLM, YLM) = (0, 0, 0)
      
      self.SetPVManually(self.MTRG_boardName, f"ILM_{link_id}", ILM)
      if link_id not in ["L", "R", "U"]:
        self.SetPVManually(self.MTRG_boardName, f"XLM_{link_id}", XLM)
        self.SetPVManually(self.MTRG_boardName, f"YLM_{link_id}", YLM)
      else:
        self.SetPVManually(self.MTRG_boardName, f"LINK_{link_id}_PROPAGATE_F3", Propagate)
        self.SetPVManually(self.MTRG_boardName, f"LINK_{link_id}_PROPAGATE_F4", Propagate)
        self.SetPVManually(self.MTRG_boardName, f"LINK_{link_id}_PROPAGATE_F5", Propagate)
        self.SetPVManually(self.MTRG_boardName, f"LINK_{link_id}_PROPAGATE_F6", Propagate)
        self.SetPVManually(self.MTRG_boardName, f"LINK_{link_id}_PROPAGATE_F7", Propagate)
          
    
    print("################ 1H: Turn master Tpwr, Rpwr all on, disable line & local loopback") 

    linkIDList = ["A","B","C","D","E","F","G","H","L","R","U"]

    for link_id in linkIDList:
      self.SetPVManually(self.MTRG_boardName, f"TPwr_{link_id}", 1)
      self.SetPVManually(self.MTRG_boardName, f"RPwr_{link_id}", 1)
      self.SetPVManually(self.MTRG_boardName, f"SLoL_{link_id}", 0)
      self.SetPVManually(self.MTRG_boardName, f"SLiL_{link_id}", 0)

    self.SetPVManually(self.MTRG_boardName, "reg_SERDES_LOCAL_LE", 0)
    self.SetPVManually(self.MTRG_boardName, "reg_SERDES_LINE_LE", 0)

    print("################ 1I: Turn on Master Trigger line drivers and set pre-emphasis")

    pvValList = [
       ["PrE_0", 1],
       ["PrE_1", 1],
       ["PrE_2", 1],
       ["PEHLRU", 0],
       ["PEEFG", 0],
       ["PEABCD", 0],
       ["RESET_LINK_INIT", 0] 
    ]
    for pv_name, value in pvValList:
      self.SetPVManually(self.MTRG_boardName, pv_name, value)

    print("######################################################## End of Stage 1")


  #^>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
  def Stage2_Setup(self):
    print(">>>>>>>>>>>>>>>>>>>>> Stage 2 setup: Initialize all Routers to receive clock and SYNC from Master Trigger")

    for rtr_name in self.RTR_boardName_list:
      print(f"################ 2A: Setting up Router {rtr_name}")

      print(" Setting router to use local clock")
      self.SetPVManually(rtr_name, "ClkSrc", 0)
      self.SetPVManually(rtr_name, "reg_FORCE_SYNC_REG", 0)

      print("setting up router to drive SYNC back to Master Trigger")
      self.SetPVManually(rtr_name, "LRUCtl00", 0)
      self.SetPVManually(rtr_name, "LRUCtl01", 0)
      self.SetPVManually(rtr_name, "LRUCtl02", 0)
      self.SetPVManually(rtr_name, "LRUCtl00", 1)
      self.SetPVManually(rtr_name, "LRUCtl01", 1)
      self.SetPVManually(rtr_name, "LRUCtl02", 1)

      print("etting up rounter link pre-emphasis")
      self.SetPVManually(rtr_name, "PrE_0", 0)
      self.SetPVManually(rtr_name, "PrE_1", 0)
      self.SetPVManually(rtr_name, "PrE_2", 0)
      self.SetPVManually(rtr_name, "PrE_0", 1)
      self.SetPVManually(rtr_name, "PrE_1", 1)
      self.SetPVManually(rtr_name, "PrE_2", 1)

      self.SetPVManually(rtr_name, "PEHLRU", 0)
      self.SetPVManually(rtr_name, "PEEFG", 0)
      self.SetPVManually(rtr_name, "PEABCD", 0)

      self.SetPVManually(rtr_name, "LinkL_DCbal", 1)
      self.SetPVManually(rtr_name, "reg_SERDES_LOCAL_LE", 0)
      self.SetPVManually(rtr_name, "reg_SERDES_LINE_LE", 0)

      



      print("################ 2B: Setting Router Input Link Mask")


