class SlitherCli < Formula
  include Language::Python::Virtualenv

  desc "Colorful terminal Snake game with local high scores"
  homepage "https://github.com/DibyoD/slither-cli"
  # Point this at your GitHub release tarball once you cut a release, e.g.:
  #   https://github.com/DibyoD/slither-cli/archive/refs/tags/v1.0.0.tar.gz
  url "https://github.com/DibyoD/slither-cli/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "c18093f2ad40a81866093f9ee53793a983f880e7320839e4be01b44de76b001e"
  license "MIT"

  depends_on "python@3.12"

  # slither-cli has no third-party dependencies (pure stdlib), so there are
  # no `resource` blocks to declare here.

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "slither-cli #{version}", shell_output("#{bin}/slither-cli --version")
  end
end
