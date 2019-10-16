module makeshell_aux
import os

pub fn greet() {
  println("well, howdy!!")
}

pub fn leave() {
  exit(0)
}

struct ExecResult {
  pub:
    code int
}

pub fn exec_cmd(args []string) ?ExecResult {
  mut argv := [voidptr(0)].repeat(args.len+1)
  for i:=0; i < args.len; i++ {
    argv[i] = voidptr(args[i].str)
  }
  p := C.fork()
  if p < 0 {
    err_txt := os.get_error_msg(C.errno)
    return error("fork: $err_txt")
  }
  if p == 0 {
    C.execvp(args[0].str, byteptr(argv.data))
    err_txt := os.get_error_msg(C.errno)
    panic("execvp: $err_txt")
  }

  status := int(0)
  for {
    if C.waitpid(p, &status, 0) == -1 {
      err_txt := os.get_error_msg(C.errno)
      return error("waitpid: $err_txt")
    }
    if C.WIFEXITED(status) { return ExecResult {code: C.WEXITSTATUS(status) }}
  }
  return ExecResult {code:0}
}

pub fn run(args []string) {
  r := exec_cmd(args) or {panic(err)}
  if r.code != 0 {
    rc := r.code
    panic ("$args returned $rc")
  }
}
