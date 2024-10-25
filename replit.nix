{pkgs}: {
  deps = [
    pkgs.python310Full
    pkgs.poetry
    pkgs.geckodriver
    pkgs.chromium
    pkgs.chromedriver

  ];
}
