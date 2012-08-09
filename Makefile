all:
	python ./pyrser/parsing/cpp/setup.py build_ext --inplace
	mv ./asciiParse.so ./pyrser/parsing/cpp
	rm -rf build
