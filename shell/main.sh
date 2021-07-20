#!/usr/bin/env bash
root_dir=/jd/own
js_dir=/jd/own/imwcc_jd_imwcc/js
shell_dir=/jd/own/imwcc_jd_imwcc/shell


if [ ! -x "$root_dir"]; then
  echo "$root_dir 不存在"
  retrun -1
fi
if [ ! -x "$js_dir"]; then
  echo "$js_dir 不存在"
  retrun -1
fi
if [ ! -x "$shell_dir"]; then
  echo "$shell_dir 不存在"
  retrun -1
fi

. $shell_dir/replace_js.sh
. $shell_dir/sed_code.sh
. $shell_dir/replace_shell.sh
. $shell_dir/daemon_task.sh

pip3 install -r $root_dir/pythonProjects/requirements.txt

# python task
echo "python task begin"
python3 $root_dir/pythonProjects/combine_all_crontable.py
python3 $root_dir/pythonProjects/JD_tencent_scf_to_jd_scripts/switch_shop_id.py
echo "python task end"

