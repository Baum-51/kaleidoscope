# Kaleidoscope Phase1 設計仕様書

## 1. 第一段階システム概要

静止画像を入力として異世界風の風景を生成する。

第二段階以降ではカメラ映像をリアルタイム変換することを想定しており、  
Phase1では入力された画像を数秒以内に変換し、  
**レンズ越しに異世界を見ている感覚をユーザーに提供すること**を目的とする。

---

# 2. システム構成

## フロントエンド

React

役割

- 画像アップロード
- 世界観選択
- 変換結果表示

---

## バックエンド

FastAPI + C++

役割

- 画像解析
- 世界変換処理
- 画像生成

---

# 3. デプロイ構成

## AWS

### フロントエンド

CloudFront

### バックエンド

EC2 on ECS

### ユーザー管理

Cognito

認証方式

PKCE

---

# 4. ユースケース

1. ユーザーが変換先の世界観を選択  
2. 画像をアップロード  
3. 異世界風画像を生成  
4. 画像を表示  

---

# 5. 機能要件

## 5.1 画像入力機能

入力形式

- JPG
- PNG

最大サイズ

- 3MB

---

## 5.2 出力される世界

### 魔法世界

特徴

- 紫系カラーフィルタ
- 光粒子
- グロー効果

---

### 人類滅亡100年後の世界

特徴

- 緑系カラー補正
- 建物に植物テクスチャ
- 霧エフェクト

---

## 5.3 世界変換機能

### 入力

- 静止画像
- 変換先世界タイプ

### 出力

- 異世界風に変換された画像

---

## 5.4 結果表示機能

Reactで以下を表示

- 変換前画像
- 変換後画像

表示形式

- 横並び表示

追加機能

- 画像ダウンロード

---

# 6. 非機能要件

## パフォーマンス

レスポンス

- 3秒以内

処理対象画像

- 最大 1024×1024

---

## セキュリティ

- ファイルサイズ制限
- MIMEタイプ検証
- ユーザー認証（PKCE）

---

# 7. API設計

## POST /auth/login

入力

- PKCE challenge
- redirect uri

---

## POST /auth/logout

入力

- redirect uri
- refresh token cookie

---

## POST /transform

入力

multipart/form-data

- image
- world_type

出力

- image/png

---

# 8. 画像処理設計

Phase1ではAIを使用せず、  
**画像処理ベースの変換パイプライン**を採用する。

---

## 画像処理パイプライン


input image
↓
preprocessing
↓
scene segmentation
↓
world transform
↓
effect overlay
↓
image compositing
↓
output image


---

## 8.1 preprocessing

処理

- resize
- noise reduction
- normalize

目的

- 処理時間の短縮
- 画像品質の安定化

---

## 8.2 scene segmentation

画像を意味のある領域に分割する

例

- 空
- 建物
- 植物
- 道路

方法

- edge detection
- threshold segmentation
- color clustering

---

## 8.3 world transform

領域ごとに世界観に応じた変換を行う

### 魔法世界

処理

- カラーマッピング
- グロー処理
- コントラスト強調

---

### 人類滅亡世界

処理

- 緑系カラーフィルタ
- テクスチャ合成
- 彩度低下

---

## 8.4 effect overlay

追加エフェクト

### 魔法世界

- 粒子エフェクト
- 光の筋

### 人類滅亡世界

- 霧
- 埃

---

## 8.5 image compositing

複数のレイヤーを合成

方法

- alpha blending

---

# 9. フロントエンド設計


auth
├ login page
├ pkce
├ login callback
└ logout callback

pages
└ Home


Home画面

- 世界選択
- 画像アップロード
- 結果表示

---

# 10. バックエンド設計


app
├ main.py
├ routers
│ ├ transform.py
│ └ auth.py
├ services
│ └ world_transform.py
├ models
└ config.py


---

# 11. エラーハンドリング

- 400 invalid image
- 413 file too large
- 401 unauthorized
- 500 transform error

---

# 12. 開発環境

## フロントエンド

- React
- Vite
- TypeScript

---

## バックエンド

- Python 3.13+
- FastAPI
- OpenCV
- NumPy

高速処理

- C++
- OpenCV

---

# 13. テスト方針

## ユーザー認証

- PKCE認証テスト

---

## 画像処理

- 変換結果テスト
- 処理時間テスト

---

## 統合テスト

- Frontend ↔ Backend通信
- APIレスポンス