.PHONY: all run view clean

TARGET = main.tex
LUAL   = lualatex -shell-escape

all: run

run: $(TARGET)
	$(LUAL) $(TARGET)
	$(LUAL) $(TARGET)

view: run
	evince main.pdf