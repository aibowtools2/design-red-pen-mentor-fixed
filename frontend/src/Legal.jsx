import React, { useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';

const Legal = () => {
    const { hash } = useLocation();

    useEffect(() => {
        if (hash) {
            const element = document.getElementById(hash.replace('#', ''));
            if (element) {
                element.scrollIntoView({ behavior: 'smooth' });
            }
        } else {
            window.scrollTo(0, 0);
        }
    }, [hash]);

    const sectionStyle = {
        marginBottom: '60px',
        background: 'rgba(255, 255, 255, 0.1)',
        padding: '40px',
        borderRadius: '24px',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
    };

    const h2Style = {
        color: '#00ccff',
        marginBottom: '30px',
        borderBottom: '2px solid rgba(0, 204, 255, 0.3)',
        paddingBottom: '10px',
    };

    const pStyle = {
        lineHeight: '1.8',
        color: 'rgba(255, 255, 255, 0.9)',
        marginBottom: '15px',
        fontSize: '0.95rem'
    };

    return (
        <div className="dashboard" style={{ padding: '60px 20px', maxWidth: '1000px', margin: '0 auto', minHeight: '100vh', background: '#0a0a0a' }}>
            <header style={{ textAlign: 'center', marginBottom: '60px' }}>
                <h1 className="title" style={{ fontSize: '2.5rem', marginBottom: '10px' }}>リーガル情報</h1>
                <Link to="/" style={{ color: '#00ccff', textDecoration: 'none', fontWeight: 'bold' }}>
                    ← ホームに戻る
                </Link>
            </header>

            {/* 1. 利用規約 */}
            <section id="terms" style={sectionStyle}>
                <h2 style={h2Style}>利用規約</h2>
                <div style={pStyle}>
                    <p>第1条 (目的)<br />本規約は、当方が提供する本サービス「デザイン赤ペン先生」の利用条件を定めるものです。</p>
                    <p>第2条 (利用資格)<br />本サービスを利用するには、本規約に同意する必要があります。</p>
                    <p>第3条 (禁止事項)<br />
                        ・本サービスへの不正アクセスやデータの改ざん<br />
                        ・本ソフトウェアのリバースエンジニアリング、逆コンパイル、または逆アセンブル<br />
                        ・当方または第三者の著作権、商標権等の知的財産権を侵害する行為
                    </p>
                    <p>第4条 (免責事項)<br />
                        ・当方は、本サービスを利用したことにより生じた損害について、一切の責任を負いません。<br />
                        ・本サービスの動作保証は行っておらず、予告なく内容の変更や停止を行う場合があります。
                    </p>
                    <p>第5条 (規約の変更)<br />当方は、必要と判断した場合には、いつでも本規約を変更することができるものとします。</p>
                </div>
            </section>

            {/* 2. プライバシーポリシー */}
            <section id="privacy" style={sectionStyle}>
                <h2 style={h2Style}>プライバシーポリシー</h2>
                <div style={pStyle}>
                    <p>1. 情報の収集<br />
                        ・LINE User ID（公式LINE経由での利用時）<br />
                        ・利用状況データ（サービス改善および機能向上のため）
                    </p>
                    <p>2. 情報の利用目的<br />
                        ・本サービスの円滑な提供および維持<br />
                        ・サービスの改善および新機能の開発<br />
                        ・ユーザーサポートの提供
                    </p>
                    <p>3. 第三者への提供<br />
                        法令に基づく場合を除き、お客様の同意なく個人情報を第三者に提供することはありません。
                    </p>
                    <p>4. お問い合わせ<br />
                        プライバシーポリシーに関するお問い合わせは、サポート窓口（support@aibowtools.com）までご連絡ください。
                    </p>
                </div>
            </section>

            {/* 3. 特定商取引法に基づく表記 */}
            <section id="legal" style={sectionStyle}>
                <h2 style={h2Style}>特定商取引法に基づく表記</h2>
                <table style={{ width: '100%', borderCollapse: 'collapse', color: 'rgba(255, 255, 255, 0.9)' }}>
                    <tbody>
                        {[
                            ['販売事業者名', 'AiBow Tools'],
                            ['代表者', '請求があり次第提供致しますので、必要な方はお問い合わせください。'],
                            ['所在地', '〒150-0044 東京都渋谷区円山町5番3号 MIEUX渋谷ビル8階'],
                            ['お問い合わせ先', 'support@aibowtools.com'],
                            ['販売価格', 'プレミアムプラン 月額 350円（税込）'],
                            ['商品代金以外の必要料金', 'なし（通信料はお客様負担）'],
                            ['お支払い方法', 'クレジットカード決済 (Stripe)'],
                            ['サービスの提供時期', '決済完了後、直ちにご利用いただけます。'],
                            ['返品・キャンセル', 'サービスの性質上、決済完了後の返品・キャンセルはお受けできません。']
                        ].map(([label, value]) => (
                            <tr key={label} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                                <td style={{ padding: '15px', fontWeight: 'bold', width: '30%' }}>{label}</td>
                                <td style={{ padding: '15px' }}>{value}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </section>

            <footer style={{ textAlign: 'center', paddingBottom: '40px', color: 'rgba(255, 255, 255, 0.5)' }}>
                <p>&copy; {new Date().getFullYear()} AiBow Tools</p>
            </footer>
        </div>
    );
};

export default Legal;
