with import <up> {}; {
  pyEnv = stdenv.mkDerivation {
    name = "py";
    buildInputs = with python3Packages; [ stdenv python pyopenssl pyyaml flask virtualenv psutil requests2 ];
  };
}
