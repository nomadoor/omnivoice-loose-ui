# omnivoice-loose-ui

[![English README](https://img.shields.io/badge/README-English-1f1f1f?style=flat-square)](./README.md)

## Original OmniVoice

これは OmniVoice 用のローカル UI です。

- 元リポジトリ: https://github.com/k2-fsa/OmniVoice
- モデルや本体仕様は、まず元リポジトリを確認してください。

## これは何か

OmniVoice 用の小さいローカル Web UI です。

- 左: ジョブ履歴
- 右: 現在の生成設定
- 下: テキスト入力欄

チャットアプリではありません。入力テキスト 1 件が生成ジョブ 1 件になります。

## セットアップ

```bat
install.bat
```

## 起動

```bat
run.bat
```

オプション:

```bat
run.bat --no-browser
run.bat --port 9000
run.bat --port 9000 --no-browser
```

開発用:

```bat
run-dev.bat
```

## 基本操作

1. アプリを開く。
2. 言語 / reference audio / voice instruction / speed / duration / num step を設定する。
3. 下の入力欄にテキストを書く。
4. `Run` か `Ctrl/Cmd + Enter` を押す。
5. ジョブが `queued -> running -> done / error` と進むのを待つ。
6. 完了したら `Play` または `Download` を使う。

## Reference Audio

- ドラッグ＆ドロップ、またはファイル選択で読み込めます。
- アップロードした音声は `backend/uploads` に保存されます。
- 保存済みの reference audio は dropdown から再選択できます。

## メモ

- 初回起動時はモデルのダウンロードが走ることがあります。
- Hugging Face の cache は `backend/hf-cache` に保存されます。
- 生成音声は `backend/generated` に保存されます。
- アプリ状態は `backend/state.json` に保存されます。
