import os
import sys
import config
import getopt
import config
from probset import probset_factory
from utils import file_util, config_util, logger_util
from TaskTBeval import TaskTBeval

def get_probset(problem_config):
    probset_config = problem_config.autoline.probset
    probset_paras = {
        "path": probset_config.path,
        "more_info_paths": probset_config.more_info_paths,
        "only_tasks": probset_config.only,
        "exclude_tasks": probset_config.exclude,
        "filter_content": probset_config.filter[0]
    }
    probset_paras["more_info_paths"] = probset_config.more_info_paths
    if probset_config.gptgenRTL_path is not None:
        probset_paras["more_info_paths"].append(probset_config.gptgenRTL_path)
    if probset_config.mutant_path is not None:
        probset_paras["more_info_paths"].append(probset_config.mutant_path)
    problem_set = probset_factory.create_probset(probset_config.name, probset_paras)
    if probset_config.exclude != []:
        problem_set.del_items(probset_config.exclude, del_by_list=True)
    return problem_set

def main():
    problem_config = config_util.load_config_to_obj(config.PROBLEM_CONFIG_PATH)
    logger_util.logger = logger_util.setup_logger("AutoEval", problem_config.save.root)
    problem_set = get_probset(problem_config)
    run_info = []
    for idx, probdata_single in enumerate(problem_set.data):
        task_id = probdata_single["task_id"]
        logger_util.logger.info("############ task {} [{}] ############".format(idx+1, task_id))
        task_dir = os.path.join(problem_config.save.root, task_id)

        code_dir = os.path.join(task_dir, "TBgen_codes")
        i = 1
        debug_code_dir = code_dir
        tmp_code_dir = os.path.join(task_dir, "debug_{}".format(i))
        while os.path.exists(tmp_code_dir) or os.path.exists(tmp_code_dir+"_reboot"):
            if os.path.exists(tmp_code_dir):
                debug_code_dir = tmp_code_dir
            elif os.path.exists(tmp_code_dir+"_reboot"):
                debug_code_dir = tmp_code_dir+"_reboot"
            i += 1
            tmp_code_dir = os.path.join(task_dir, "debug_{}".format(i))

        if not os.path.exists(task_dir) or not os.path.exists(code_dir):
        # if not os.path.exists(task_dir):
            logger_util.logger.error("Task {} directory does not exist, skip\n".format(task_id))
            continue
        if os.path.exists(os.path.join(debug_code_dir, "{}_tb.v".format(task_id))):
            TB_code_v = file_util.read_file_to_str(os.path.join(debug_code_dir, "{}_tb.v".format(task_id)))
        else:
            TB_code_v = file_util.read_file_to_str(os.path.join(code_dir, "{}_tb.v".format(task_id)))
        if os.path.exists(os.path.join(debug_code_dir, "{}_tb.py".format(task_id))):
            TB_code_py = file_util.read_file_to_str(os.path.join(debug_code_dir, "{}_tb.py".format(task_id)))
        else:
            TB_code_py = file_util.read_file_to_str(os.path.join(code_dir, "{}_tb.py".format(task_id)))
        # TB_code_v = file_util.read_file_to_str(os.path.join(task_dir, "final_TB.v"))
        # TB_code_py = file_util.read_file_to_str(os.path.join(task_dir, "final_TB.py"))
        evaluator = TaskTBeval(
            task_id,
            task_dir,
            TB_code_v,
            probdata_single.get("testbench", None),
            probdata_single.get("module_code", None),
            probdata_single.get("mutants", None),
            None,
            True,
            TB_code_py,
            True
        )
        evaluator.run()
        logger_util.logger.info("")

        info_out = {
            "task_id": task_id,
            "taks_number": idx + 1,
        }
        if evaluator.Eval0_exist:
            info_out.update({
                "Eval0_pass": evaluator.Eval0_pass,
                "Eval0_iv_pass": evaluator.Eval0_iv_pass
            })
        if evaluator.Eval1_exist:
            info_out.update({"Eval1_pass": evaluator.Eval1_pass})
        if evaluator.Eval2_exist:
            info_out.update({
                "Eval2_pass": evaluator.Eval2_pass,
                "Eval2_ratio": "%d/%d"%(len(evaluator.Eval2_passed_mutant_idx), len(probdata_single['mutants'])),
                "Eval2_failed_mutant_idxes": evaluator.Eval2_failed_mutant_idx
            })
        if evaluator.Eval2b_exist:
            info_out.update({
                "Eval2b_pass": evaluator.Eval2b_pass,
                "Eval2b_ratio": "%d/%d"%(len(evaluator.Eval2b_passed_mutant_idx), len(probdata_single['gptgen_RTL'])),
                "Eval2b_failed_mutant_idxes": evaluator.Eval2b_failed_mutant_idx
            })
        if evaluator.Eval0_pass and evaluator.Eval1_pass and evaluator.Eval2_pass:
            info_out.update({"full_pass": True})
        run_info.append(info_out)
    run_info_path = os.path.join(problem_config.save.root, "run_info.json")
    file_util.write_json_file(run_info, run_info_path)

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:c:", ["help", "config="])
    except getopt.GetoptError:
        print("Invalid command")
        sys.exit(2)
    if len(opts) == 1:
        opt, arg = opts[0]
        if opt in ("-h", "--help"):
            print("Usage: python main.py [-h] [-c custom_config_path]\n\nOptions:\n  -h, --help\t\t\tShow this help message and exit\n  -c, --config\tRun the main function with the custom config file in config/custom.yaml\n\nIf no command, run the main function with the custom config file in config/custom.yaml\n")
            sys.exit()
        elif opt in ("-c", "--config"):
            config.PROBLEM_CONFIG_PATH = arg
        else:
            print("Invalid command")
            sys.exit(2)
        main()
    else:
        print("Invalid command")
        sys.exit(2)