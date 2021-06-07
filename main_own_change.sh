#!/usr/bin/env bash

work_dir=/jd/own/imwcc_jd_imwcc
. $work_dir/apply_replace_own_file.sh
. $work_dir/custom_code.sh
. $work_dir/apply_default_help_code.sh
. $work_dir/hang_up_task.sh

pip3 install -r $work_dir/pythonProjects/JD_tencent_scf_to_jd_scripts/requirements.txt
#转换JD-SCRIPT
python3 $work_dir/pythonProjects/combine_all_crontable.py

python3 $work_dir/pythonProjects/JD_tencent_scf_to_jd_scripts/switch_shop_id.py

