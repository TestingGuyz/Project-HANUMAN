{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "hanuman-env";
  
  buildInputs = with pkgs; [
    # Python runtime
    python311
    python311Packages.pip
    python311Packages.virtualenv
    
    # Audio processing
    portaudio
    ffmpeg
    libsndfile
    libopus
    
    # Development tools
    git
    curl
    wget
    
    # System libraries
    stdenv.cc.cc.lib
    zlib
  ];
  
  shellHook = ''
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║             🔱 PROJECT HANUMAN - DIVINE VOICE ASSISTANT 🔱      ║"
    echo "║                    NixOS Development Shell                     ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Create virtual environment
    if [ ! -d ".venv" ]; then
      echo "⚡ Creating Python virtual environment..."
      python3.11 -m venv .venv
      echo "✅ Virtual environment created"
    fi
    
    # Activate venv
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
    
    # Check for .env file
    if [ ! -f ".env" ]; then
      echo ""
      echo "⚠️  No .env file found. Creating from template..."
      cp .env.example .env
      echo "✅ .env created. Please edit and add your API keys:"
      echo ""
      echo "   REQUIRED:"
      echo "   - GROQ_API_KEY (https://console.groq.com)"
      echo "   - ELEVENLABS_API_KEY (https://elevenlabs.io)"
      echo ""
      echo "   OPTIONAL:"
      echo "   - TAVILY_API_KEY (for Khoj mode)"
      echo "   - HUGGINGFACE_TOKEN (for advanced STT)"
      echo ""
      echo "   Edit with: nano .env"
      echo ""
    else
      echo "✅ .env file found"
    fi
    
    # Install dependencies
    echo ""
    echo "📦 Checking Python dependencies..."
    if [ ! -f ".venv/pip-installed" ]; then
      echo "Installing packages from requirements.txt..."
      pip install --upgrade pip setuptools wheel > /dev/null 2>&1
      pip install -r requirements.txt > /dev/null 2>&1
      touch .venv/pip-installed
      echo "✅ Dependencies installed"
    else
      echo "✅ Dependencies already installed"
    fi
    
    echo ""
    echo "🚀 HANUMAN is ready! Commands:"
    echo ""
    echo "   Start server:    python main.py"
    echo "   Open browser:    http://localhost:5000"
    echo "   View logs:       tail -f logs/*.log"
    echo "   Test API:        curl http://localhost:5000/status"
    echo ""
    echo "   Or just say... 'python main.py' and open your browser!"
    echo ""
    echo "🙏 Jai Shri Ram!"
    echo ""
  '';
  
  # Environment variables
  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
    pkgs.stdenv.cc.cc
    pkgs.zlib
    pkgs.portaudio
  ];
}
