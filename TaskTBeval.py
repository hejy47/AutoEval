"""
Description :   This is the testbench eval stage in autoline
Author      :   Ruidi Qiu (r.qiu@tum.de)
Time        :   2024/7/24 11:24:43
LastEdited  :   2024/8/28 21:08:21
"""


import os
import iverilog_call as iv
import python_call as py
from utils.logger_util import logger

TC_PASS_CHECK_LIST_TB_GEN = ["All test cases passed", "all test cases passed", "All Test Cases Passed"]
TC_PASS_CHECK_LIST_TB_GOLDEN = ['Mismatches: 0 in ', 'Hint: Total mismatched samples is 0 out of']
TC_PASS_CHECK_LIST_PYCHECKER = ["[]"]

class TaskTBeval():
    """
    ### description
    - this is the evaluation stage of our pipeline; the priority of this stage is that TB is generated and the empty DUT compilation is passed;
    - please use `try` to catch the exception of this function.
    - this module is independent from the previous modules.
    #### input
    - task_id: the name of the problem
    - root_dir: the dir of one problem
    - TB_gen: the testbench under evaluation (str)
    - TB_golden: the golden testbench (str)
    - DUT_golden: the golden RTL DUT (str)
    - DUT_mutant_list: the list of RTL DUT mutants modified from DUT_golden;[str]        
    #### output
    - dict
        - "Eval1_pass" : bool (whether the golden RTL checking passed)
        - "Eval2_pass" : bool (whether the golden TB comparison on RTL mutants passed)
        - "Eval2_failed_mutant_idxes" : list of int (the index of the failed mutants)
    """
    """main structure: run(), run_Eval1(), run_Eval2()"""
    def __init__(self, task_id: str, task_dir: str, TB_gen: str, TB_golden:str=None, DUT_golden:str=None, DUT_mutant_list:list=None, DUT_gptgen_list:list = None, pychecker_en:bool = False, pychecker_code:str = "", runfiles_save:bool = True):
        self.task_id = task_id
        self.task_dir = task_dir
        self.TB_gen = TB_gen
        self.TB_golden = TB_golden
        self.DUT_golden = DUT_golden
        self.DUT_mutant_list = DUT_mutant_list
        self.DUT_gptgen_list = DUT_gptgen_list
        self.pychecker_en = pychecker_en
        self.save_en = runfiles_save
        self.TB_gen_mode = "TB_gen" if not self.pychecker_en else "Pychecker"
        self.pychecker_code = pychecker_code
        self.working_dir = ""
        # Eval1 related
        self.Eval1_exist = False
        # self.Eval1_dir = task_dir + "eval1_GoldenRTL/"
        self.Eval1_dir = os.path.join(task_dir, "eval1_GoldenRTL")
        self.Eval1_results = None
        self.Eval1_pass = None
        # Eval2 related
        self.Eval2_exist = False
        # self.Eval2_dir = task_dir + "eval2_GoldenTB_and_mutants/"
        self.Eval2_dir = os.path.join(task_dir, "eval2_GoldenTB_and_mutants")
        self.Eval2_pass = None
        self.Eval2_failed_mutant_idx = None
        self.Eval2_passed_mutant_idx = None
        # Eval2b related
        self.Eval2b_exist = False
        # self.Eval2b_dir = task_dir + "eval2b_GPTgenTB/"
        self.Eval2b_dir = os.path.join(task_dir, "eval2b_GPTgenTB")
        self.Eval2b_pass = None
        self.Eval2b_failed_mutant_idx = None
        self.Eval2b_passed_mutant_idx = None

    # @log_localprefix("TBeval")
    def run(self):
        # Eval 1
        if self.DUT_golden is not None:
            self.run_Eval1()
        if self.Eval1_pass:
            # Eval 2
            if self.TB_golden is not None and self.DUT_mutant_list is not None:
                self.run_Eval2(mode="mutant")
            # Eval 2b
            if self.TB_golden is not None and self.DUT_gptgen_list is not None:
                self.run_Eval2(mode="gptgen")
        else:
            logger.info("[%s] Eval 2/2b is skipped because Eval 1 failed" % (self.task_id)) 
        self.clean_wave_vcd() # some golden TBs may generate wave.vcd files
    
    def run_Eval1(self):
        silent = True
        ### Eval 1: Golden RTL checking
        logger.info("[%s] Eval 1: Golden RTL checking begins" % (self.task_id))
        self.Eval1_pass = self.run_testbench(self.Eval1_dir, self.TB_gen, self.DUT_golden, self.TB_gen_mode, self.pychecker_code, raise_when_fail=True, save_en=self.save_en)
        logger.info("[%s] Eval 1: Golden RTL checking %s!" % (self.task_id, "passed" if self.Eval1_pass else "failed"))
        # my_log = logger.positive if self.Eval1_pass else logger.failed
        # my_log("[%s] Eval 1: Golden RTL checking %s!" % (self.task_id, "passed" if self.Eval1_pass else "failed"))
        self.Eval1_exist = True

    def run_Eval2(self, mode:str="mutant"):
        """ mode: "mutant" or "gptgen" """
        silent = True
        assert mode in ["mutant", "gptgen"], "Invalid mode in run_Eval2: " + mode
        if mode == "mutant": # Eval2
            print_str = "[%s] Eval 2: Golden TB checking on RTL mutants" % (self.task_id)
            mutant_subdir_name = "mutant"
            DUT_list = self.DUT_mutant_list
            eval_dir = self.Eval2_dir
        elif mode == "gptgen": # Eval2b
            print_str = "[%s] Eval 2b: Golden TB checking on GPT generated RTL codes" % (self.task_id)
            mutant_subdir_name = "gptgen_DUT"
            DUT_list = self.DUT_gptgen_list
            eval_dir = self.Eval2b_dir
        ### Eval 2: Golden TB comparison on RTL mutants
        logger.info(print_str)
        mutant_results = []
        for idx, DUT_mutant in enumerate(DUT_list):
            # mutant_subdir = eval_dir + "%s_%d/"%(mutant_subdir_name, idx+1)
            mutant_subdir = os.path.join(eval_dir, "%s_%d"%(mutant_subdir_name, idx+1))
            # GoldenTB_subsubdir = mutant_subdir + "GoldenTB/"
            GoldenTB_subsubdir = os.path.join(mutant_subdir, "GoldenTB")
            # GenedTB_subsubdir = mutant_subdir + "GeneratedTB/"
            GenedTB_subsubdir = os.path.join(mutant_subdir, "GeneratedTB")
            try: #in case the mutant has syntax error
                TBgolden_pass = self.run_testbench(GoldenTB_subsubdir, self.TB_golden, DUT_mutant, "TB_golden", save_en=self.save_en)
            except:
                TBgolden_pass = False
            try:
                TBgen_pass = self.run_testbench(GenedTB_subsubdir, self.TB_gen, DUT_mutant, self.TB_gen_mode, self.pychecker_code, save_en=self.save_en)
            except:
                TBgen_pass = False
            if not TBgolden_pass and not TBgen_pass:
                mutant_pass = True
            elif TBgolden_pass and TBgen_pass:
                mutant_pass = True
            else:
                mutant_pass = False
            mutant_results.append(mutant_pass)
        eval_pass = all(mutant_results)
        failed_mutant_idx = [idx + 1 for idx, result in enumerate(mutant_results) if not result]
        passed_mutant_idx = [idx + 1 for idx, result in enumerate(mutant_results) if result]
        if mode == "mutant":
            self.Eval2_pass, self.Eval2_failed_mutant_idx, self.Eval2_passed_mutant_idx, self.Eval2_exist = eval_pass, failed_mutant_idx, passed_mutant_idx, True
        elif mode == "gptgen":
            self.Eval2b_pass, self.Eval2b_failed_mutant_idx, self.Eval2b_passed_mutant_idx, self.Eval2b_exist = eval_pass, failed_mutant_idx, passed_mutant_idx, True
        result = "perfectly passed" if eval_pass else ("finished (%d/%d)" % (len(passed_mutant_idx), len(mutant_results)))
        logger.info("%s %s!" % (print_str, result))

    def run_testbench(self, dir, TB_code, DUT_code, TB_type, pychecker_code = "", raise_when_fail = False, save_en = True):
        """
        it has two mode: pychecker mode or verilog testbench mode
        -input:
            - dir: the dir to save the TB, DUT and pychecker code
            - TB_code: str; the testbench code
            - DUT_code: str; the DUT code
            - TB_type: str: TB_gen, TB_golden, Pychecker
            - pychecker_code: str; the pychecker code
        - output:
            - pass: bool; if the DUT passed the testbench
        """
        # iverilog part
        # save the TB and DUT
        assert TB_type in ["TB_gen", "TB_golden", "Pychecker"], "Invalid TB_type in run_testbench: " + TB_type
        os.makedirs(dir, exist_ok=True)
        self.working_dir = dir
        with open(self.TB_path, "w") as f:
            f.write(TB_code)
        with open(self.DUT_path, "w") as f:
            f.write(DUT_code)
        iv_run_info = iv.iverilog_call_and_save(dir, silent=True)
        if raise_when_fail:
            assert iv_run_info[0], "%s Iverilog Compilation Failed: the PREREQUISITE of 'Evaluation' is no syntactic error from Testbench!!!"%(TB_type)
        # pychecker part (if enabled)
        if TB_type == "Pychecker":
            with open(self.PY_path, "w") as f:
                f.write(pychecker_code)
            py_run_info = py.python_call_and_save(pypath=self.PY_path, silent=True)
            if raise_when_fail:
                assert py_run_info[0], "%s Python Compilation Failed: the PREREQUISITE of 'Evaluation' is no syntactic error from Python code!!!"%(TB_type)
            # check if the DUT passed the testbench
            TC_pass = self.TC_pass_from_TC_out(sim_pass=True, sim_out=py_run_info[1]["out"], TB_type="Pychecker") & iv_run_info[0] & py_run_info[0]
        else:
            TC_pass = self.TC_pass_from_TC_out(sim_pass=True, sim_out=iv_run_info[4]["out"], TB_type=TB_type) & iv_run_info[0]
        if not save_en:
            # os.system(f"rm -rf {dir}")
            cmd = f"find {dir} -type f ! -name 'run_info*'" + r" -exec rm -f {} +"
            os.system(cmd)
        return TC_pass

    def clean_wave_vcd(self):
        """clean the .vcd files in the task_dir"""
        # clean_dir = self.task_dir[:-1] if self.task_dir.endswith("/") else self.task_dir
        clean_dir = self.task_dir
        for root, dirs, files in os.walk(clean_dir):
            for file in files:
                # clean wave.vcd
                if file.endswith(".vcd"):
                    os.remove(os.path.join(root, file))

    @property
    def TB_path(self):
        # return self.working_dir + self.task_id + "_tb.v"
        return os.path.join(self.working_dir, self.task_id + "_tb.v")
    
    @property
    def DUT_path(self):
        # return self.working_dir + self.task_id + ".v"
        return os.path.join(self.working_dir, self.task_id + ".v")
    
    @property
    def PY_path(self):
        # return self.working_dir + self.task_id + "_tb.py"
        return os.path.join(self.working_dir, self.task_id + "_tb.py")

    @staticmethod
    def TC_pass_from_TC_out(sim_pass: bool, sim_out: str, TB_type="TB_gen"):
        """
        get the information if DUT passed all the test cases from the testbench
        #### input
        - sim_pass: bool; if TB passed the compilation. if not, will return False without check
        - sim_out: the simulation output message;
        - TB_ty: "TB_gen" or "TB_golden" or "Pychecker"; the type of the testbench
        """
        if not sim_pass:
            return False
        assert TB_type in ["TB_gen", "TB_golden", "Pychecker"], "Invalid TB_type during 'TC_pass_from_TC_out': " + TB_type
        tc_pass_check_list_dict = {"TB_gen": TC_PASS_CHECK_LIST_TB_GEN, "TB_golden": TC_PASS_CHECK_LIST_TB_GOLDEN, "Pychecker": TC_PASS_CHECK_LIST_PYCHECKER}
        tc_pass_check_list = tc_pass_check_list_dict[TB_type]
        if TB_type in ["TB_gen", "TB_golden"]:
            for check_str in tc_pass_check_list:
                if check_str in sim_out:
                    return True
            return False
        elif TB_type in ['Pychecker']:
            # check if the last [] contains any element
            # find the last ] in the out
            last_bracket_end = sim_out.rfind("]")
            # find the last [ in the out
            last_bracket_start = sim_out.rfind("[")
            # check if the last bracket pair is "[]", containing no element
            if (last_bracket_end - last_bracket_start) == 1:
                return True
            else:
                return False
