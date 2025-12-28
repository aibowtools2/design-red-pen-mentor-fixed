(function() {
    // -------------------------------------------------------------------------
    // NARUHODO DESIGN - ANIMATED SUMMARY GENERATOR
    // -------------------------------------------------------------------------

    // アンドゥグループの開始
    app.beginUndoGroup("Naruhodo Design Summary Gen");

    try {
        // 1. INPUT DATA (JSON Representation)
        // ---------------------------------------------------------------------
        var bookData = {
            "title": "なるほどデザイン (Naruhodo Design)",
            "subtitle": "A Comprehensive Guide to Practical Design Principles",
            "chapters": [
                {
                    "topic": "Case A: Design for Beginners",
                    "principle": "Clarity & Accessibility",
                    "type": "clarity"
                },
                {
                    "topic": "Tool 1: Importance Scale",
                    "principle": "Prioritization (Visual Hierarchy)",
                    "type": "scale"
                },
                {
                    "topic": "Tool 2: Spotlight",
                    "principle": "Focus through Contrast",
                    "type": "spotlight"
                },
                {
                    "topic": "Tool 3: Personification",
                    "principle": "Brand Personality (Shape/Style)",
                    "type": "personality"
                },
                {
                    "topic": "Tool 6: Magnifying Glass",
                    "principle": "Attention to Detail (Alignment)",
                    "type": "detail"
                }
            ],
            "insight": "Effective design is TRANSLATION.\nCognitive frameworks to ensure the viewer says:\n'Naruhodo!' (I see!)",
            "palette": {
                "bg": [245/255, 245/255, 220/255], // Beige #F5F5DC
                "text": [51/255, 51/255, 51/255],   // Dark #333333
                "accent": [255/255, 215/255, 0/255], // Gold #FFD700
                "blue": [135/255, 206/255, 235/255], // SkyBlue #87CEEB
                "pink": [255/255, 182/255, 193/255]  // Pink #FFB6C1
            }
        };

        // 2. CONFIGURATION & HELPERS
        // ---------------------------------------------------------------------
        var compW = 1920;
        var compH = 1080;
        var fps = 24;
        var sceneDuration = 4; // seconds per scene
        var totalDuration = (bookData.chapters.length + 2) * sceneDuration; // Intro + Chapters + Outro

        // コンポジション作成関数
        function createMainComp(name, w, h, pixelAspect, duration, frameRate) {
            var item = app.project.items.addComp(name, w, h, pixelAspect, duration, frameRate);
            return item;
        }

        // 背景レイヤー作成関数
        function addSolid(comp, name, colorArr) {
            var solid = comp.layers.addSolid(colorArr, name, comp.width, comp.height, 1);
            solid.moveToEnd();
            return solid;
        }

        // テキストレイヤー作成ヘルパー
        function addText(comp, content, size, colorArr, pos, timeStart, duration) {
            var txtLayer = comp.layers.addText(content);
            var txtProp = txtLayer.property("Source Text");
            var txtDoc = txtProp.value;
            
            txtDoc.fontSize = size;
            txtDoc.fillColor = colorArr;
            txtDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
            txtProp.setValue(txtDoc);
            
            // アンカーポイントを中央に簡易調整 (ビジュアル上の中心)
            // 注: 正確な矩形取得は複雑なため、ここでは配置座標で調整
            txtLayer.position.setValue(pos);
            
            txtLayer.inPoint = timeStart;
            txtLayer.outPoint = timeStart + duration;
            
            // フェードインアニメーション
            txtLayer.opacity.setValueAtTime(timeStart, 0);
            txtLayer.opacity.setValueAtTime(timeStart + 0.5, 100);
            txtLayer.opacity.setValueAtTime(timeStart + duration - 0.5, 100);
            txtLayer.opacity.setValueAtTime(timeStart + duration, 0);
            
            return txtLayer;
        }

        // シェイプ作成ヘルパー (矩形・楕円)
        function createShape(comp, type, size, pos, color, name) {
            var shapeLayer = comp.layers.addShape();
            shapeLayer.name = name;
            var shapeGroup = shapeLayer.property("Contents").addProperty("ADBE Vector Group");
            
            // 形状の追加
            var shapePath;
            if (type === "rect") {
                shapePath = shapeGroup.property("Contents").addProperty("ADBE Vector Shape - Rect");
                shapePath.property("Size").setValue(size);
            } else if (type === "ellipse") {
                shapePath = shapeGroup.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
                shapePath.property("Size").setValue(size);
            }
            
            // 塗りの追加
            var fill = shapeGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");
            fill.property("Color").setValue(color);
            
            shapeLayer.position.setValue(pos);
            return shapeLayer;
        }

        // 3. MAIN EXECUTION
        // ---------------------------------------------------------------------
        
        // メインコンポジションの生成
        var mainComp = createMainComp("Naruhodo Design Summary", compW, compH, 1, totalDuration, fps);
        
        // 背景色の適用 (和紙っぽいベージュ)
        addSolid(mainComp, "Background", bookData.palette.bg);

        var currentTime = 0;

        // --- SCENE 1: INTRO ---
        // タイトルとサブタイトルの表示
        addText(mainComp, bookData.title, 120, bookData.palette.text, [compW/2, compH/2 - 50], currentTime, sceneDuration);
        addText(mainComp, bookData.subtitle, 40, bookData.palette.text, [compW/2, compH/2 + 60], currentTime, sceneDuration);
        
        currentTime += sceneDuration;

        // --- SCENE 2...N: CHAPTER LOOPS ---
        // 各章のデザイン原則をアニメーションで表現
        
        for (var i = 0; i < bookData.chapters.length; i++) {
            var chapter = bookData.chapters[i];
            
            // 章のタイトル表示 (上部)
            addText(mainComp, chapter.principle, 60, bookData.palette.text, [compW/2, 150], currentTime, sceneDuration);
            addText(mainComp, chapter.topic, 30, [0.5, 0.5, 0.5], [compW/2, 220], currentTime, sceneDuration);

            // 原則ごとのアニメーションロジック
            switch (chapter.type) {
                
                case "clarity":
                    // ケースA: 整理整頓 (グリッドに整列するアニメーション)
                    for (var r = 0; r < 2; r++) {
                        for (var c = 0; c < 2; c++) {
                            var box = createShape(mainComp, "rect", [200, 200], [compW/2 + (c-0.5)*220, compH/2 + (r-0.5)*220 + 50], bookData.palette.blue, "GridBox");
                            box.inPoint = currentTime;
                            box.outPoint = currentTime + sceneDuration;
                            
                            // ランダムな位置から整列
                            var startPos = [box.position.value[0] + (Math.random()*400 - 200), box.position.value[1] + (Math.random()*400 - 200)];
                            var endPos = box.position.value;
                            
                            box.position.setValueAtTime(currentTime, startPos);
                            box.position.setValueAtTime(currentTime + 1, endPos);
                            box.opacity.setValueAtTime(currentTime, 0);
                            box.opacity.setValueAtTime(currentTime + 0.5, 100);
                        }
                    }
                    break;

                case "scale":
                    // ツール1: 重要度天秤 (サイズの対比)
                    var small1 = createShape(mainComp, "ellipse", [150, 150], [compW/2 - 300, compH/2 + 50], [0.7,0.7,0.7], "Small1");
                    var big = createShape(mainComp, "ellipse", [150, 150], [compW/2, compH/2 + 50], bookData.palette.accent, "Big");
                    var small2 = createShape(mainComp, "ellipse", [150, 150], [compW/2 + 300, compH/2 + 50], [0.7,0.7,0.7], "Small2");
                    
                    var shapes = [small1, big, small2];
                    for(var k=0; k<shapes.length; k++){
                        shapes[k].inPoint = currentTime;
                        shapes[k].outPoint = currentTime + sceneDuration;
                    }

                    // 真ん中だけ巨大化させる
                    big.scale.setValueAtTime(currentTime + 0.5, [100, 100]);
                    big.scale.setValueAtTime(currentTime + 1.5, [250, 250]); // Bounce effect
                    big.scale.setValueAtTime(currentTime + 2.0, [200, 200]);
                    break;

                case "spotlight":
                    // ツール2: スポットライト (色による強調)
                    for (var x = -2; x <= 2; x++) {
                        var dotColor = (x === 0) ? bookData.palette.accent : [0.8, 0.8, 0.8];
                        var dot = createShape(mainComp, "ellipse", [100, 100], [compW/2 + (x*150), compH/2 + 50], [0.8, 0.8, 0.8], "Dot");
                        dot.inPoint = currentTime;
                        dot.outPoint = currentTime + sceneDuration;
                        
                        if(x === 0) {
                            // 中央だけ色が変わる
                            var content = dot.property("Contents").property(1).property("Contents");
                            var fillProp = content.property("ADBE Vector Graphic - Fill").property("Color");
                            fillProp.setValueAtTime(currentTime + 0.5, [0.8, 0.8, 0.8]);
                            fillProp.setValueAtTime(currentTime + 1.0, bookData.palette.accent);
                            
                            // 少し上に浮く
                            dot.position.setValueAtTime(currentTime + 1.0, [compW/2, compH/2 + 50]);
                            dot.position.setValueAtTime(currentTime + 1.5, [compW/2, compH/2 + 20]);
                        }
                    }
                    break;

                case "personality":
                    // ツール3: 擬人化 (形状のモーフィング - Roundness)
                    var morphShape = createShape(mainComp, "rect", [300, 300], [compW/2, compH/2 + 50], bookData.palette.pink, "MorphShape");
                    morphShape.inPoint = currentTime;
                    morphShape.outPoint = currentTime + sceneDuration;
                    
                    var rectPath = morphShape.property("Contents").property(1).property("Contents").property(1);
                    var roundness = rectPath.property("Roundness");
                    
                    // 四角(堅い) -> 丸(柔らかい)
                    roundness.setValueAtTime(currentTime + 0.5, 0);
                    roundness.setValueAtTime(currentTime + 2.5, 150);
                    break;

                case "detail":
                    // ツール6: 虫眼鏡 (整列の微調整)
                    var line1 = createShape(mainComp, "rect", [400, 20], [compW/2, compH/2 - 50], bookData.palette.text, "Line1");
                    var line2 = createShape(mainComp, "rect", [400, 20], [compW/2 + 40, compH/2 + 50], bookData.palette.text, "Line2"); // ずれている
                    var line3 = createShape(mainComp, "rect", [400, 20], [compW/2 - 20, compH/2 + 150], bookData.palette.text, "Line3"); // ずれている

                    var lines = [line1, line2, line3];
                    for(var l=0; l<lines.length; l++){
                        lines[l].inPoint = currentTime;
                        lines[l].outPoint = currentTime + sceneDuration;
                    }

                    // ピシッと揃うアニメーション
                    line2.position.setValueAtTime(currentTime + 0.5, [compW/2 + 40, compH/2 + 50]);
                    line2.position.setValueAtTime(currentTime + 1.5, [compW/2, compH/2 + 50]);

                    line3.position.setValueAtTime(currentTime + 0.5, [compW/2 - 20, compH/2 + 150]);
                    line3.position.setValueAtTime(currentTime + 1.5, [compW/2, compH/2 + 150]);
                    break;
            }

            currentTime += sceneDuration;
        }

        // --- SCENE 3: CONCLUSION ---
        // 結論（インサイト）の表示
        var textLayer = addText(mainComp, bookData.insight, 50, bookData.palette.text, [compW/2, compH/2], currentTime, sceneDuration);
        
        // テキストボックスのように整形（簡易的）
        // 注: スクリプトでの段落テキスト制御は複雑なため、改行コードで対応済みと仮定
        
        // 完了メッセージ
        alert("Naruhodo Design Summary Generated Successfully!\nなるほどデザインの概要アニメーションが作成されました。");

    } catch (err) {
        alert("Error: " + err.toString() + "\nLine: " + err.line);
    } finally {
        app.endUndoGroup();
    }

})();