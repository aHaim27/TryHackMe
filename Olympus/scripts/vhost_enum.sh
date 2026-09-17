wordlist="/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt"
total=$(wc -l < "$wordlist")
counter=$(mktemp)

echo 0 > "$counter"
echo "[*] Starting VHost scan: $total candidates"

cat "$wordlist" | xargs -P 20 -I {} bash -c '
    sub="$1"
    counter="$2"
    total="$3"

    location=$(curl -s --max-time 3 -o /dev/null -w "%{redirect_url}" \
        -H "Host: ${sub}.olympus.thm" \
        http://olympus.thm/)

    # Safely increment shared counter
    (
        flock -x 200
        current=$(cat "$counter")
        current=$((current + 1))
        echo "$current" > "$counter"

        printf "\r[*] Progress: %d/%d (%d%%)" \
            "$current" "$total" "$((current * 100 / total))"
    ) 200>"${counter}.lock"

    # Show deviations from baseline
    if [[ -n "$location" && "$location" != "http://olympus.thm/" ]]; then
        printf "\n[+] %s.olympus.thm -> %s\n" "$sub" "$location"
    fi
' _ {} "$counter" "$total"

echo
echo "[+] Scan complete"
rm -f "$counter" "${counter}.lock"
