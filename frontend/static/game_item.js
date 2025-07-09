// アイテム即時発動
window.useItemImmediately = function(itemName, targetDigit = null) {
    if (!itemName) return;
    // 既に使用済みなら無効
    const btn = document.querySelector(`button[data-item="${itemName}"]`);
    if (btn && btn.classList.contains('used')) return;
    // TARGETの場合は数字が必要
    if (itemName === 'TARGET' && (targetDigit === null || targetDigit === undefined)) {
        alert('TARGETアイテムを使う場合は数字を選択してください。');
        return;
    }
    fetch('/use-item', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_name: itemName, target_digit: targetDigit })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert('アイテム使用に失敗しました: ' + data.error);
            return;
        }
        // メッセージ表示
        if (typeof showItemResult === 'function') {
            showItemResult(data.effect || 'アイテム効果が実行されました');
        }
        // アイテムボタンをグレーアウト
        if (btn) {
            btn.classList.remove('selected');
            btn.classList.add('used');
        }
        // 履歴をリロード
        location.reload();
    })
    .catch(err => {
        alert('アイテム使用中にエラーが発生しました');
        console.error(err);
    });
};

window.selectItemButton = function(btn) {
    if (btn.classList.contains('used')) return;
    const item = btn.dataset.item;
    if (item === 'TARGET') {
        document.getElementById('target-ui').style.display = 'block';
        document.querySelectorAll('.digit-btn').forEach(dbtn => {
            dbtn.onclick = function() {
                const digit = parseInt(this.textContent);
                document.getElementById('target-digit-input').value = digit;
                window.useItemImmediately('TARGET', digit);
                document.getElementById('target-ui').style.display = 'none';
            };
        });
    } else {
        window.useItemImmediately(item);
    }
};

// アイテム効果のメッセージ表示（game.html側のshowItemResultを利用） 