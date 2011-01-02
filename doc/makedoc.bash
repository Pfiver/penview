#!/bin/bash -e

cd "${0%/*}/"

penview=$PWD/..
ghpages=$PWD/gh-pages

_makedoc() {
	if ! [ -d "$ghpages" ]
	then
		echo 'run "$0 --gh-pages-setup" first' >&2
		exit 1
	fi
	rm -rf "$ghpages/epydoc"
	mkdir -p "$ghpages/epydoc"
	export PYTHONPATH="$penview/lib"
	epydoc -v -o "$ghpages/epydoc" --no-private --docformat restructuredtext --name PenView --url http://p2000.github.com/penview/ "$penview"/*.py
	read -p "git add commit push ? "
	[[ "$REPLY" == [yY]* ]] || exit
	cd "$ghpages"
	git add .
	git commit --amend -C HEAD
	git push
}

_gh-pages-setup() {
	mkdir "$ghpages"
	cd "$ghpages"
	git init
	cat > .git/config <<-EOF
		[core]
		 	repositoryformatversion = 0
		 	logallrefupdates = true
		 	autocrlf = false
		 	filemode = true
		[remote "origin"]
		 	url = ssh://git@github.com/P2000/penview.git
		 	push = refs/heads/gh-pages:refs/heads/gh-pages
		 	fetch = refs/heads/gh-pages:refs/remotes/origin/gh-pages
		[branch "gh-pages"]
		 	remote = origin
		 	merge = refs/heads/gh-pages
	EOF
	git pull
}

case "$1"
in
	"") _makedoc
	;;
	--gh-pages-setup) _gh-pages-setup
	;;
	*) echo "usage: $0 [--gh-pages-setup]"
	;;
esac
