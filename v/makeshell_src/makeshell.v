import os

fn leave(ec int, tmp string) {
    os.system("rm -rf $tmp")
    exit(ec)
}


fn main() {
  if os.args.len == 2 {
    line := "/********************************************************/"
    head := "/******************** this is line 0 ********************/"
    foot := "/******* previous line was the last provided line *******/"
    src := "import os\nimport makeshell_aux as msa\n" +
      "fn main() {\n$line\n"+
      "$head\n" +
      os.args[1] +
      "\n$foot\n$line\n}\n"

    cc := os.getenv('ms_cc')
    ms_cc_extra := os.getenv('ms_cc_extra')
    ms_verbose := os.getenv('ms_verbose') == "true"

    user := os.getenv('USER')
    tmp0 := "${user}.recipe-temp.${C.getpid()}/"
    tmp := "/dev/shm/$tmp0"
    os.mkdir_all(tmp)

    srcfile_v := tmp + "src.v"
    srcfile_c := tmp + "src.c"
    recipe_exe := tmp + "recipe.exe"

    os.write_file(srcfile_v, src)

    v_cmd := "v -o $srcfile_c $srcfile_v"
    if ms_verbose { println(v_cmd) }
    rc_v := os.exec(v_cmd) or { panic(err) }
    if rc_v.exit_code != 0 {
      os.system("cat -n $srcfile_v")
      println("--------")
      println(rc_v.output)
      leave(rc_v.exit_code,tmp)
    }

    cc_cmd := "$cc $ms_cc_extra -o $recipe_exe $srcfile_c -lm"
    if ms_verbose { println(cc_cmd) }
    rc_c := os.exec(cc_cmd) or { panic(err) }
    if rc_c.exit_code != 0 {
      println(rc_c.output)
      os.system("mv $tmp $tmp0")
      println("c source moved from $tmp to $tmp0")
      exit(rc_c.exit_code)
    }

    leave(os.system(recipe_exe),tmp)
  }
}
