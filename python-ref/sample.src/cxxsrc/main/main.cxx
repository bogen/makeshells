#if SAMPLE_MAIN == 1
#define SAMPLE_main main
#else
#define SAMPLE_main yk4_main
#endif

int SAMPLE_main(int argc, const char** argv) {
  printf("%s: %d\n", argv[0], argc);
  return 0;
}
