import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './App.css';

const Landing = () => {
    const navigate = useNavigate();

    // Check if already logged in - if so, redirect to app
    useEffect(() => {
        if (localStorage.getItem('token')) {
            navigate('/app');
        }
    }, [navigate]);

    // Mock Data for the Demo Section
    const mockAnalysis = {
        design_score: 35,
        detailed_metrics: {
            color_palette: { score: 2, comment: "黄色い背景に赤い文字は警告色の組み合わせであり、長時間見るには刺激が強すぎます。不快感を与える配色です。" },
            composition: { score: 3, comment: "視線誘導が全く考慮されていません。要素が散乱しており、どこから読めばいいか迷います。" },
            typography: { score: 2, comment: "複数のフォントが無秩序に混在しています。「SALE」の歪み加工も安っぽさを助長しています。" },
            contrast: { score: 4, comment: "色の差はありますが、彩度が高すぎてハレーション（目がチカチカする現象）を起こしています。" },
            balance: { score: 3, comment: "雪の結晶のクリップアートが唐突に配置されており、全体のバランスを崩しています。" },
            hierarchy: { score: 2, comment: "全ての情報が「大声」で主張しており、情報の優先順位が全くわかりません。" },
            clarity: { score: 4, comment: "「SALE」であることは伝わりますが、詳細情報（期間や対象）が読み取れません。" },
            originality: { score: 2, comment: "典型的な「素人が作ったチラシ」の域を出ておらず、ブランド価値を損なっています。" },
            relevance: { score: 5, comment: "冬のセールというテーマ自体は伝わりますが、品質への信頼感が欠如しています。" },
            impact: { score: 8, comment: "悪い意味でのインパクトは絶大です。一度見たら忘れられない「雑さ」があります。" }
        },
        good_points: [
            "遠くからでも目立つ配色のインパクトはあります",
            "冬のセールであること自体は一目で分かります",
            "情報の要素（文字、装飾）は最低限揃っています"
        ],
        google_data_insights: {
            google_fonts_recommendation: {
                suggested_font_name: "Roboto / Noto Sans JP",
                reason: "現在の歪んだ手書き風フォントは可読性を著しく低下させています。可読性の高いサンセリフ体で情報を整理しましょう。"
            },
            material_design_check: {
                metric: "Color Hierarchy",
                verdict: "FAILED",
                advice: "Material Designでは、主要なアクションにのみアクセントカラーを使用します。全面を原色で埋め尽くすのは避け、70%をベースカラー（白や淡い色）に設定してください。"
            }
        },
        improvements: [
            {
                priority: "HIGH",
                naruhodo_principle: "整列（Alignment）",
                issue: "文字の配置がバラバラで、見る人に不安感を与えます",
                suggestion: "見えないグリッド線を引き、全ての要素の左端を揃えるだけで信頼感が回復します。",
                quantitative_value: "左揃えに統一"
            },
            {
                priority: "HIGH",
                naruhodo_principle: "近接（Proximity）",
                issue: "雪のアイコンとテキストの関係性が不明確です",
                suggestion: "装飾は情報の邪魔にならない場所に移動し、関連するテキスト情報同士を近づけてグループ化してください。",
                quantitative_value: "マージンを統一"
            }
        ]
    };

    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    return (
        <div className="landing-page">
            {/* Header / Nav */}
            <nav className="lp-nav">
                <div className="logo">デザイン赤ペン先生 <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>v2.3</span></div>

                {/* Desktop Navigation */}
                <div className="nav-links desktop-only">
                    <a href="#demo" className="nav-btn">デモ体験</a>
                    <a href="#features" className="nav-btn">特徴</a>
                    <a href="#pricing" className="nav-btn">料金</a>
                    <Link to="/login" className="nav-btn">ログイン</Link>
                    <Link to="/signup" className="primary-btn landing-cta-small">無料で始める</Link>
                </div>

                {/* Mobile Hamburger Button */}
                <button className="hamburger-btn mobile-only" onClick={toggleMenu} aria-label="Menu">
                    <span className={`bar ${isMenuOpen ? 'open' : ''}`}></span>
                    <span className={`bar ${isMenuOpen ? 'open' : ''}`}></span>
                    <span className={`bar ${isMenuOpen ? 'open' : ''}`}></span>
                </button>

                {/* Mobile Menu Overlay */}
                <div className={`mobile-menu ${isMenuOpen ? 'open' : ''}`}>
                    <a href="#demo" className="mobile-nav-link" onClick={toggleMenu}>デモ体験</a>
                    <a href="#features" className="mobile-nav-link" onClick={toggleMenu}>特徴</a>
                    <a href="#pricing" className="mobile-nav-link" onClick={toggleMenu}>料金</a>
                    <div className="mobile-auth-buttons">
                        <Link to="/login" className="nav-btn mobile-auth-btn" onClick={toggleMenu}>ログイン</Link>
                        <Link to="/signup" className="primary-btn landing-cta-small mobile-auth-btn" onClick={toggleMenu}>無料で始める</Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <header className="lp-hero">
                <div className="container hero-container">
                    <div className="hero-content-left">
                        <h1 className="hero-title">あなたのデザインを、<br /><span className="highlight">3秒でスコアリング</span>。</h1>
                        <p className="hero-subtitle">
                            Googleの膨大な学習データを元に、AIがあなたの作品を客観的に評価。<br />
                            改善点を具体的に<span className="marker-highlight">「赤ペン」</span>で言語化します。
                        </p>
                        <div className="hero-actions">
                            <Link to="/signup" className="primary-btn hero-btn">今すぐ無料で試す</Link>
                            <a href="#demo" className="text-link hero-secondary-btn">添削サンプルを見る ↓</a>
                        </div>
                    </div>
                    <div className="hero-content-right desktop-only">
                        {/* Image will be placed here via CSS background or img tag */}
                        <img src="/hero_red_pen_mockup.png" alt="AI Red Pen Correction" className="hero-image-visual" />
                    </div>
                </div>
            </header>

            {/* Demo Section (Moved Up) */}
            <section id="demo" className="lp-demo-section">
                <div className="container">
                    <div className="section-header-center">
                        <span className="section-tag">Feature</span>
                        <h2 className="section-title text-center">デザイン赤ペン先生による評価</h2>
                        <p className="section-desc">AIがプロの視点で、あなたのデザインの「良い点」と「改善点」を指摘します。</p>
                    </div>

                    <div id="report-content" className="demo-report-box" style={{ padding: '0px' }}>
                        <div className="score-card">
                            <div className="score-circle" style={{ '--score': mockAnalysis.design_score }}>
                                <span className="score-value">{mockAnalysis.design_score}</span>
                            </div>
                            <p>Design Score (Mock)</p>
                        </div>

                        <main className="tensaku-grid">
                            <div className="left-col">
                                <div className="image-preview card">
                                    <img src="/images/demo_sample.png" alt="Sample Display" />
                                    <div className="image-label">添削前のサンプル画像</div>
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
                                                <div className="progress-bar-bg">
                                                    <div className="progress-bar-fill" style={{ width: `${item.score * 10}%` }}></div>
                                                </div>
                                                <p style={{ fontSize: '0.75rem', opacity: 0.7, margin: 0 }}>{item.comment}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <div className="right-col">
                                <div className="card google-data" style={{ marginBottom: '30px' }}>
                                    <h3 className="section-title">📊 Google Big Data Insights</h3>
                                    <div style={{ marginBottom: '20px' }}>
                                        <span className="google-label">Google Fonts API</span>
                                        <div className="google-font-rec">
                                            <strong>Suggested: </strong> {mockAnalysis.google_data_insights.google_fonts_recommendation.suggested_font_name}
                                        </div>
                                        <p style={{ fontSize: '0.9rem', opacity: 0.8 }}>{mockAnalysis.google_data_insights.google_fonts_recommendation.reason}</p>
                                    </div>
                                    <div>
                                        <span className="google-label">Material Design 3</span>
                                        <p style={{ color: 'var(--accent-red)', fontWeight: 'bold' }}>
                                            {mockAnalysis.google_data_insights.material_design_check.verdict}:
                                            <span style={{ color: 'white', fontWeight: 'normal', marginLeft: '10px' }}>{mockAnalysis.google_data_insights.material_design_check.advice}</span>
                                        </p>
                                    </div>
                                </div>

                                <div className="card">
                                    <h3 className="section-title">🔧 Improvement Plan</h3>
                                    {mockAnalysis.improvements.map((item, i) => (
                                        <div key={i} className="improvement-item">
                                            <div className="imp-header">
                                                <span className="imp-badge">{item.priority}</span>
                                                <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>{item.naruhodo_principle}</span>
                                            </div>
                                            <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>{item.issue}</div>
                                            <div className="imp-suggestion">
                                                {item.suggestion}
                                                {item.quantitative_value && <span className="imp-value">{item.quantitative_value}</span>}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </main>
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" className="lp-pricing">
                <div className="container">
                    <h2 className="section-title text-center">料金プラン</h2>
                    <p className="text-center" style={{ marginBottom: '40px', opacity: 0.8 }}>まずは無料で、AIの実力を体験してください。</p>

                    <div className="pricing-grid">
                        {/* Free Plan */}
                        <div className="card pricing-card free-plan">
                            <div className="plan-badge">お試し</div>
                            <h3 className="plan-name">Free Plan</h3>
                            <div className="price-display">
                                <span className="currency">¥</span>
                                <span className="amount">0</span>
                                <span className="period">/ 月</span>
                            </div>
                            <ul className="benefits-list">
                                <li>✨ <b>AIデザイン解析 (月3回まで)</b></li>
                                <li>📊 <b>基本スコアリング</b></li>
                                <li>❌ <span style={{ opacity: 0.5 }}>詳細改善プラン</span></li>
                                <li>❌ <span style={{ opacity: 0.5 }}>過去履歴の保存</span></li>
                            </ul>
                            <Link to="/signup" className="secondary-btn" style={{ width: '100%', marginTop: 'auto' }}>無料で始める</Link>
                        </div>

                        {/* Standard Plan */}
                        <div className="card pricing-card recommended-plan">
                            <div className="plan-badge recommended">人気 No.1</div>
                            <h3 className="plan-name">Standard Plan</h3>
                            <div className="price-display">
                                <span className="currency">¥</span>
                                <span className="amount">500</span>
                                <span className="period">/ 月 (税込)</span>
                            </div>
                            <ul className="benefits-list">
                                <li>✨ <b>AIデザイン解析 無制限</b></li>
                                <li>🚀 <b>優先的な解析処理</b></li>
                                <li>🔒 <b>画像データは保持しない安心設計</b></li>
                                <li>📊 <b>詳細な改善プランの提示</b></li>
                            </ul>
                            <Link to="/signup" className="primary-btn" style={{ width: '100%', marginTop: 'auto' }}>このプランで始める</Link>
                        </div>
                    </div>
                </div>
            </section>



            {/* Final CTA */}
            <section className="lp-cta">
                <h2 style={{ fontSize: '2.5rem', marginBottom: '20px' }}>デザインを磨く準備はできましたか？</h2>
                <p style={{ marginBottom: '30px', opacity: 0.8 }}>今すぐ登録して、AIメンターによる添削を体験しましょう。</p>
                <Link to="/signup" className="primary-btn" style={{ padding: '20px 60px', fontSize: '1.2rem' }}>無料でアカウントを作成</Link>
            </section>

            {/* Footer */}
            <footer className="footer lp-footer">
                <div className="footer-content">

                    <div className="footer-links">
                        <Link to="/privacy" className="footer-link">プライバシーポリシー</Link>
                        <Link to="/terms" className="footer-link">利用規約</Link>
                        <Link to="/legal" className="footer-link">特定商取引法に基づく表記</Link>
                    </div>
                    <p className="copyright">&copy; {new Date().getFullYear()} AiBow Tools. All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
};

export default Landing;
