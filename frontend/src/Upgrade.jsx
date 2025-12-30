import React, { useEffect, useState } from 'react';
// Rebuild trigger 2025-12-29
import { Link, useLocation } from 'react-router-dom';

const Upgrade = () => {
    const location = useLocation();
    const [success, setSuccess] = useState(false);
    const [uid, setUid] = useState(null);

    useEffect(() => {
        const query = new URLSearchParams(location.search);
        if (query.get('success')) {
            setSuccess(true);
        }
        // Extract User ID from URL (e.g. ?uid=U12345...)
        const userId = query.get('uid');
        if (userId) {
            setUid(userId);
        } else {
            const localUid = localStorage.getItem('user_id');
            if (localUid) setUid(localUid);
        }
    }, [location]);

    // Construct Dynamic Stripe Link
    const lineStripeUrl = "https://buy.stripe.com/fZu14macr0CH7Kh8KKaAw02"; // 350 JPY (LINE Friends)
    const webStripeUrl = "https://buy.stripe.com/14AdR8bgv5X15C90eeaAw03";  // 500 JPY (Web Standard)

    // Use 350 JPY link if user came from LINE with a UID in the URL query
    const isLineUser = new URLSearchParams(location.search).get('uid');
    const baseStripeUrl = isLineUser ? lineStripeUrl : webStripeUrl;

    const stripeUrl = uid
        ? `${baseStripeUrl}?client_reference_id=${uid}`
        : baseStripeUrl;

    if (success) {
        return (
            <div className="dashboard" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <div className="card" style={{ maxWidth: '600px', width: '100%', padding: '50px', border: '1px solid #00FF00', boxShadow: '0 0 30px rgba(0, 255, 0, 0.2)', textAlign: 'center' }}>
                    <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🎉</div>
                    <h2 style={{ fontSize: '2rem', marginBottom: '20px', color: '#00FF00' }}>プレミアムへようこそ！</h2>
                    <p style={{ fontSize: '1.2rem', lineHeight: '1.6', marginBottom: '30px' }}>
                        決済ありがとうございます。<br />
                        プレミアム機能が有効になりました。
                    </p>
                    <p style={{ fontSize: '0.9rem', opacity: 0.7, marginBottom: '30px' }}>
                        ※ 機能が反映されるまで少し時間がかかる場合があります。<br />
                        LINEボットに「プラン更新」と送ってみてください。
                    </p>
                    <Link to="/app" className="submit-btn" style={{ textDecoration: 'none', display: 'inline-block', padding: '15px 40px' }}>
                        分析を始める
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="dashboard" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
            <header className="hero">
                <h1 className="title" style={{ color: '#FFD700', textShadow: '0 0 20px rgba(255, 215, 0, 0.5)' }}>プレミアムプラン</h1>
                <p className="subtitle">AIデザイン添削が無制限に</p>
            </header>

            <div className="card" style={{ maxWidth: '600px', width: '100%', padding: '50px', border: '1px solid #FFD700', boxShadow: '0 0 30px rgba(255, 215, 0, 0.2)' }}>
                <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '20px' }}>Unlimited Access</h2>
                <div style={{ textAlign: 'center', marginBottom: '30px' }}>
                    {isLineUser ? (
                        <>
                            <div style={{ fontSize: '1.2rem', color: '#aaa', textDecoration: 'line-through', marginBottom: '5px' }}>
                                通常価格 ¥500
                            </div>
                            <div style={{ fontSize: '3.5rem', fontWeight: 'bold', color: '#FFD700', lineHeight: '1' }}>
                                ¥350 <span style={{ fontSize: '1.2rem', color: '#ccc' }}>/ 月額</span>
                            </div>
                            <div style={{ fontSize: '1rem', color: '#ff4444', fontWeight: 'bold', marginTop: '10px', background: 'rgba(255, 68, 68, 0.1)', display: 'inline-block', padding: '5px 15px', borderRadius: '20px' }}>
                                🔥 LINE友達限定割引中
                            </div>
                        </>
                    ) : (
                        <>
                            <div style={{ fontSize: '3.5rem', fontWeight: 'bold', color: '#FFD700', lineHeight: '1' }}>
                                ¥500 <span style={{ fontSize: '1.2rem', color: '#ccc' }}>/ 月額</span>
                            </div>
                            <p style={{ marginTop: '10px', opacity: 0.8 }}>Web版スタンダードプラン</p>
                        </>
                    )}
                </div>

                <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 40px 0', fontSize: '1.1rem', lineHeight: '1.8' }}>
                    <li>✨ <b>回数無制限</b> (1日の上限なし)</li>
                    <li>🚀 <b>優先的</b> な分析処理 (混雑時も優先)</li>
                    <li>🎓 <b>高度な</b> デザインアドバイス機能</li>
                </ul>

                <div style={{ textAlign: 'center' }}>
                    {/* Stripe Payment Link */}
                    <a
                        href={stripeUrl}
                        className="submit-btn"
                        style={{
                            display: 'inline-block',
                            textDecoration: 'none',
                            fontSize: '1.2rem',
                            padding: '20px 50px',
                            backgroundColor: '#FFD700',
                            color: '#000',
                            fontWeight: 'bold',
                            boxShadow: '0 0 20px rgba(255, 215, 0, 0.4)'
                        }}
                    >
                        プレミアムに参加する
                    </a>
                </div>

                <div style={{ textAlign: 'center', marginTop: '20px' }}>
                    <p style={{ fontSize: '0.8rem', opacity: 0.7 }}>Stripeで安全に決済されます</p>
                    {!uid && (
                        <p style={{ color: '#ffcc00', fontSize: '0.8rem', marginTop: '10px' }}>
                            ⚠️ 注意: LINEアプリからアクセスしないと、アカウント連携ができません。
                        </p>
                    )}
                </div>
            </div>

            {/* 注意事項セクション */}
            <div style={{ maxWidth: '600px', width: '100%', marginTop: '40px', textAlign: 'left', opacity: 0.8, fontSize: '0.85rem' }}>
                <h3 style={{ borderBottom: '1px solid #555', paddingBottom: '10px', marginBottom: '15px' }}>⚠️ 注意事項</h3>
                <ul style={{ paddingLeft: '20px', lineHeight: '1.6' }}>
                    <li>本プランは月額制のサブスクリプションです。いつでも解約可能です。</li>
                    <li>解約はStripeから届くメール、またはお問い合わせから手続き可能です。</li>
                    <li>AIの分析精度は100%を保証するものではありません。あくまでデザイン制作の補助ツールとしてご利用ください。</li>
                    <li>システムメンテナンスや障害により、一時的にサービスが利用できない場合があります。</li>
                    <li>お支払い後の返金は原則として受け付けておりません。</li>
                </ul>
            </div>

            <Link to="/app" style={{ marginTop: '30px', color: '#fff', opacity: 0.7 }}>
                ← ホームに戻る
            </Link>
        </div>
    );
};

export default Upgrade;
