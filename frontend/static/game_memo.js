// メモ機能の状態管理
let memoData = {};

function toggleMemo(number) {
    const button = document.getElementById(`memo-${number}`);
    if (memoData[number]) {
        // メモがある場合は削除
        delete memoData[number];
        button.classList.remove('has-memo');
        button.title = '';
    } else {
        // メモがない場合は追加
        memoData[number] = true;
        button.classList.add('has-memo');
        button.title = 'メモ付き';
    }
    saveMemoData();
}

function updateMemoButton(number) {
    const button = document.getElementById(`memo-${number}`);
    if (memoData[number]) {
        button.classList.add('has-memo');
        button.title = 'メモ付き';
    } else {
        button.classList.remove('has-memo');
        button.title = '';
    }
}

function saveMemoData() {
    localStorage.setItem('numeronMemoData', JSON.stringify(memoData));
}

function loadMemoData() {
    const saved = localStorage.getItem('numeronMemoData');
    if (saved) {
        memoData = JSON.parse(saved);
        // 全ての数字ボタンを更新
        for (let i = 0; i <= 9; i++) {
            updateMemoButton(i);
        }
    }
}

function resetMemoData() {
    memoData = {};
    localStorage.removeItem('numeronMemoData');
    // 全ての数字ボタンをリセット
    for (let i = 0; i <= 9; i++) {
        updateMemoButton(i);
    }
}

// メモリセットフラグをチェックする関数
function checkMemoReset() {
    // URLパラメータからメモリセットフラグをチェック
    const urlParams = new URLSearchParams(window.location.search);
    const memoReset = urlParams.get('memo_reset');
    
    if (memoReset === 'true') {
        resetMemoData();
        // URLからパラメータを削除
        urlParams.delete('memo_reset');
        const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
        window.history.replaceState({}, '', newUrl);
    } else {
        loadMemoData();
    }
} 