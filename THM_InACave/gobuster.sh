for method in GET POST PUT DELETE HEAD OPTIONS; do
	echo "Method: $method"
	gobuster dir -m $method --wordlist /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt --timeout 4s -x txt,log,php,html,js,json,jsx,eml -t 50 -u 10.48.189.50 >> inacave.gob.txt
done
