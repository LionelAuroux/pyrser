%.pdf: %.mkd
	pandoc --template ../lse.template --to beamer -o $@ $^
