import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './App.css';

const Demo = () => {
    const navigate = useNavigate();

    // Mock Data for Demo
    const mockAnalysis = {
        design_score: 42,
        detailed_metrics: {
            color_palette: { score: 3, comment: "原色が強すぎて目に優しくありません。色の彩度を下げるか、ベースカラーを落ち着いた色にしましょう。" },
            composition: { score: 4, comment: "要素が中央に寄りすぎており、周辺の余白が活かせていません。" },
            typography: { score: 3, comment: "標準フォントのままで、セールのワクワク感が伝わりにくいです。" },
            contrast: { score: 5, comment: "赤と白の対比はありますが、文字の可読性が低い箇所があります。" },
            balance: { score: 4, comment: "左右のバランスが崩れており、視線が迷子になります。" },
            hierarchy: { score: 3, comment: "どれが一番重要な情報（セール価格なのか、期間なのか）が分かりにくいです。" },
            clarity: { score: 5, comment: "伝えたいことは分かりますが、整理整頓が必要です。" },
            originality: { score: 2, comment: "素材集をそのまま置いたような印象で、ブランドらしさが欠けています。" },
            relevance: { score: 6, comment: "冬のクリアランスという目的には合っています。" },
            impact: { score: 4, comment: "パッと見た時のインパクトはありますが、質の高さは感じられません。" }
        },
        good_points: [
            "セールの力強さは伝わる配色です",
            "商品の写真が中央にあり、何が売りたいかは明確です",
            "大きな赤いバースト形状が目を引きます"
        ],
        google_data_insights: {
            google_fonts_recommendation: {
                suggested_font_name: "Montserrat / Noto Sans JP",
                reason: "よりモダンで信頼感のある印象を与えるために、力強いゴシック体の組み合わせを推奨します。"
            },
            material_design_check: {
                metric: "Color Contrast Ratio",
                verdict: "FAILED",
                advice: "背景の黄色と白の文字のコントラストが3.0:1を下回っています。背景を濃くするか、文字を黒にしましょう。"
            }
        },
        improvements: [
            {
                priority: "HIGH",
                naruhodo_principle: "整列と近接",
                issue: "セールの文字と価格がバラバラに配置されています",
                suggestion: "情報をグループ化（近接）させ、ベースラインを揃える（整列）ことで読みやすさが劇的に向上します。",
                quantitative_value: "余白を24px以上確保"
            },
            {
                priority: "MEDIUM",
                naruhodo_principle: "フォントのジャンプ率",
                issue: "全ての文字が同じくらいの大きさです",
                suggestion: "一番見せたい「50% OFF」を極端に大きくし、補足情報を小さくすることで、情報の優先度を明確にします。",
                quantitative_value: "文字サイズ比を2.5倍以上に"
            }
        ]
    };

    return (
        <div className="dashboard">
            <div className="demo-banner">
                これはデモ画面です。会員登録すると、ご自身の画像で同じような解析が可能です！
                <Link to="/signup" className="demo-signup-link">無料で新規登録</Link>
            </div>

            <header className="hero">
                <h1 className="title">AIデザイン添削サンプル</h1>
                <p className="subtitle">プロの視点であなたのデザインを数値化・言語化します</p>
                <div style={{ marginTop: '20px' }}>
                    <Link to="/login" className="primary-btn" style={{ textDecoration: 'none', display: 'inline-block', padding: '10px 30px' }}>
                        ログインして自分の画像を試す
                    </Link>
                </div>
            </header>

            <div id="report-content" style={{ padding: '0px' }}>
                <div className="score-card">
                    <div className="score-circle" style={{ '--score': mockAnalysis.design_score }}>
                        <span className="score-value">{mockAnalysis.design_score}</span>
                    </div>
                    <p>Design Score</p>
                </div>

                <main className="tensaku-grid">
                    <div className="left-col">
                        <div className="image-preview card">
                            <img src="/images/demo_sample.png" alt="Sample Before" />
                            <div className="image-label">添削前のデザイン（サンプル）</div>
                        </div>

                        <div className="card" style={{ marginTop: '30px' }}>
                            <h3 className="section-title">📉 10項目 詳細スコア</h3>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                                {Object.entries(mockAnalysis.detailed_metrics).map(([key, item]) => (
                                    <div key={key} style={{ background: 'rgba(255,255,255,0.05)', padding: '10px', borderRadius: '8px' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                                            <span style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{key}</span>
                                            <span style={{ color: 'var(--accent-green)', fontWeight: 'bold' }}>{item.score}/10</span>
                                        </div>
                                        <div style={{ width: '100%', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginBottom: '5px' }}>
                                            <div style={{ width: `${item.score * 10}%`, height: '100%', background: 'var(--accent-green)', borderRadius: '2px' }}></div>
                                        </div>
                                        <p style={{ fontSize: '0.75rem', opacity: 0.7, margin: 0 }}>{item.comment}</p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="card" style={{ marginTop: '30px' }}>
                            <h3 className="section-title">👍 Good Points</h3>
                            {mockAnalysis.good_points.map((point, i) => (
                                <div key={i} className="good-point">
                                    <span>✅</span>
                                    <span>{point}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="right-col">
                        <div className="card google-data" style={{ marginBottom: '30px' }}>
                            <h3 className="section-title">📊 Google Big Data Insights</h3>
                            <div style={{ marginBottom: '20px' }}>
                                <span className="google-label">Google Fonts API</span>
                                <div className="google-font-rec">
                                    <strong>Suggested: </strong>
                                    {mockAnalysis.google_data_insights.google_fonts_recommendation.suggested_font_name}
                                </div>
                                <p style={{ fontSize: '0.9rem', opacity: 0.8 }}>
                                    {mockAnalysis.google_data_insights.google_fonts_recommendation.reason}
                                </p>
                            </div>
                            <div>
                                <span className="google-label">Material Design 3</span>
                                <p><strong>Check:</strong> {mockAnalysis.google_data_insights.material_design_check.metric}</p>
                                <p style={{ color: 'var(--accent-red)', fontWeight: 'bold' }}>
                                    {mockAnalysis.google_data_insights.material_design_check.verdict}:
                                    <span style={{ color: 'white', fontWeight: 'normal', marginLeft: '5px' }}>
                                        {mockAnalysis.google_data_insights.material_design_check.advice}
                                    </span>
                                </p>
                            </div>
                        </div>

                        <div className="card">
                            <h3 className="section-title">🔧 Improvement Plan</h3>
                            {mockAnalysis.improvements.map((item, i) => (
                                <div key={i} className="improvement-item">
                                    <div className="imp-header">
                                        <span className="imp-badge">{item.priority} Priority</span>
                                        <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>{item.naruhodo_principle}</span>
                                    </div>
                                    <div>{item.issue}</div>
                                    <div className="imp-suggestion">
                                        {item.suggestion}
                                        {item.quantitative_value && (
                                            <span className="imp-value">{item.quantitative_value}</span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </main>
            </div>

            <div style={{ textAlign: 'center', margin: '60px 0' }}>
                <h2 style={{ marginBottom: '20px' }}>あなたのデザインも、プロ級に。</h2>
                <Link to="/signup" className="primary-btn" style={{ textDecoration: 'none', display: 'inline-block', padding: '15px 50px', fontSize: '1.2rem' }}>
                    無料で今すぐ登録する
                </Link>
            </div>
        </div>
    );
};

export default Demo;
