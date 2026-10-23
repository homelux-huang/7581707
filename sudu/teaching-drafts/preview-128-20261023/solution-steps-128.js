/* DRAFT ONLY; not approved, not deployed. */
window.PREVIEW_STEP_BY_STEP_DRAFT = {
  "schemaVersion": 1,
  "scopeTotal": 128,
  "byQuestion": {
    "數學 B|7": {
      "questionId": "115-00-MB-07",
      "subject": "數學 B",
      "questionNumber": 7,
      "answerCandidate": "B",
      "aiAnswer": "B",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "a 為 2026° 最大負同界角；b 為 −115° 最小正同界角；點座標 (tan(a−b),sin(a+b))",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "同界角 θ+360°k；由角所在象限判斷三角函數正負：tan第二、第四象限負，sin第二象限正",
          "why": "同界角縮減與正負判斷，不須查實際 tan/sin 小數值。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "2026°−5×360°=226°",
          "why": "先把 2026 度減去完整的五圈。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "a=226°−360°=−134°",
          "why": "在所有負同界角中，−134° 最大（最接近0）。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "b=−115°+360°=245°",
          "why": "在所有正同界角中，245° 最小。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "a−b=−134°−245°=−379°；−379°+360°=−19°",
          "why": "化成便於判斷符號的同界角。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "tan(−19°)<0",
          "why": "−19° 位於第四象限，正切值為負。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "a+b=−134°+245°=111°；sin111°>0",
          "why": "111° 位於第二象限，正弦值為正。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "(tan(a−b),sin(a+b))=(負,正)，第二象限",
          "why": "套用座標象限正負定義。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "第二象限；單位：角度單位 °；座標三角函數值無單位；選項：B",
          "why": "把 2026° 的 226° 當負同界角；或忽略 tan(a−b) 的負號。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "75599abe2d8e2232eb13d49cf31908f05a9c8b9fb3d170453d75a0e29f8f11d9",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|9": {
      "questionId": "115-00-MB-09",
      "subject": "數學 B",
      "questionNumber": 9,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "L₁:4x+(a+5)y−10=0 通過(a,1)；L₂斜率 m₂=−1/2；L₃過(a,1)，L₃⊥L₂",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "通過(x₁,y₁)的點斜式 y−y₁=m(x−x₁)；垂直 m₂m₃=−1",
          "why": "先求已知點，再用垂直的負倒數關係建立直線方程式。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "4a+(a+5)(1)−10=0",
          "why": "因(a,1)在L₁上，座標需滿足L₁方程式。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "5a+5−10=0 ⇒ 5a−5=0 ⇒ a=1",
          "why": "整理得點座標(1,1)。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "(−1/2)×m₃=−1 ⇒ m₃=2",
          "why": "垂直直線的斜率互為負倒數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "y−1=2(x−1)",
          "why": "使用通過(1,1)、斜率2的點斜式。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "y−1=2x−2 ⇒ y=2x−1 ⇒ 2x−y−1=0",
          "why": "整理至題目選項中的一般式，得 A。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "2x−y−1=0；單位：無單位（座標軸單位未指定）；選項：A",
          "why": "垂直誤用同斜率或正倒數；a=1 未先求就亂帶點。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "f2c0430dfea667e165f7961b7318e0cde0d28f3f2007fccc4aed4e4ac6ca2b10",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|10": {
      "questionId": "115-00-MB-10",
      "subject": "數學 B",
      "questionNumber": 10,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "籤筒甲、乙、丙各一支，等機率；每次抽後將籤放回；抽取三次，求三次全非甲",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "P(單次非甲)=2/3；獨立三次全非甲=(2/3)³",
          "why": "有放回的等可能獨立抽樣，計算連續多次發生相同類型事件的機率。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "非甲籤=乙、丙，共2支；總數=3支",
          "why": "單次抽中非甲的有利結果2種，總可能3種。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "P(單次沒有甲)=2/3",
          "why": "每支籤被抽到的機率相等。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "因每次抽後放回，三次獨立、每次機率維持2/3",
          "why": "放回讓籤筒內容不變，事件機率可相乘。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "P(三次皆非甲)=(2/3)×(2/3)×(2/3)=2³/3³=8/27",
          "why": "三次『都』成立且獨立，取三事件機率乘積。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "選 C；核對補事件 P(至少一次甲)=1−8/27=19/27",
          "why": "辨識 D 是另一個事件，避免誤選。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "8/27；單位：機率（無單位）；選項：C",
          "why": "把有放回當不放回；算兩次得4/9；用補事件19/27卻忘了題目問『都沒抽到甲』。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "3c06c677c7362cbf22e792cdcbd990a584129b929d25cd63efb98037a390b7c4",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|11": {
      "questionId": "115-00-MB-11",
      "subject": "數學 B",
      "questionNumber": 11,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "f(x)=4(x+2)³+b(x+2)²+c(x+2)+d；g(x)=4x³+3x²+2x+1；f≡g",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "設 t=x+2，x=t−2，展開 g(t−2)，按同次方比較係數。",
          "why": "換元後比較同次方係數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "設t=x+2 ⇒ x=t−2",
          "why": "t 是將(x+2)視為單一變數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "g(t−2)=4(t−2)³+3(t−2)²+2(t−2)+1",
          "why": "把g中的x一律換成t−2。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "=4(t³−6t²+12t−8)+3(t²−4t+4)+2t−4+1",
          "why": "完整展開立方與平方。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "=4t³+(−24+3)t²+(48−12+2)t+(−32+12−4+1)",
          "why": "依相同次方合併係數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "=4t³−21t²+38t−23 ⇒ b=−21、c=38",
          "why": "恆等多項式相同次方係數一致。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "b+c=−21+38=17（D）",
          "why": "求題目指定的兩係數和。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "17；單位：無單位；選項：D",
          "why": "漏展開立方的一次項或誤把原式3與2直接當b,c。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "c2f2c57d0d65abc757c35e560f6ed8ce1114a452f9bae59e174e904fbb047f92",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|12": {
      "questionId": "115-00-MB-12",
      "subject": "數學 B",
      "questionNumber": 12,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "abc≠0；2x+3y=4、ax+by=c有無限多組解",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "無限解 ⇒ (a,b,c)=k(2,3,4)，k≠0；代回變更後聯立式，檢查相交/平行。",
          "why": "利用聯立式的線性相依性與消元判斷解數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "a=2k，b=3k，c=4k，k≠0",
          "why": "無限解代表同一直線且k不為零。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "A：1000k(2x+3y)=4k ⇒2x+3y=0.004，平行無解",
          "why": "左側倍數與右側不相同。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "B：k(2x+3y)=4000k ⇒2x+3y=4000，平行無解",
          "why": "右側倍數與左側不相同。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "C/D：1000(2k)x+(3k)y=4k ⇒2000x+3y=4",
          "why": "只有x係數增加1000倍。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "與2x+3y=4相減：1998x=0 ⇒x=0",
          "why": "兩條不平行線的消元可求出唯一x。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "3y=4 ⇒ y=4/3，唯一解，D正確",
          "why": "代回求y，證明是唯一解。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "D；唯一解 (0,4/3)；單位：座標無單位；選項：D",
          "why": "把只調整左邊當成等式兩邊都乘1000。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "ee793a1135e53ef1080af2b67724d9672f74028372f7ba5b607525886a621cb2",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "經濟學|26": {
      "questionId": "115-09-2-26",
      "subject": "經濟學",
      "questionNumber": 26,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "每家 Qs＝−10＋20P；同樣廠商數 N＝10；市場價格 P＝5",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "Q_市場＝N×Qs(P)＝10×(−10＋20P)",
          "why": "將相同價格下各家廠商的供給量水平加總，求整體市場供給。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "每家 Qs＝−10＋20×5",
          "why": "以題目給定市場價格5代入單一家供給函數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "20×5＝100",
          "why": "先計算價格變動項。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "每家 Qs＝−10＋100＝90",
          "why": "每家在P=5下供給90單位。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "Q_市場＝90×10＝900",
          "why": "市場有十家同樣供給者，加總其數量。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "亦可 Q_市場＝10(−10＋20P)＝−100＋200P",
          "why": "整條市場供給函數由每家函數水平加總。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "P=5 ⇒ Q_市場＝−100＋200×5＝900",
          "why": "用市場函數再次驗算數值一致。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "900；單位：荔枝供給數量單位（題幹未明訂斤／公斤）；選項：D",
          "why": "只得90忘乘10，或市場函數未將20P係數乘10。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "5b4426ed72ed5fa16e65625976465dcfc771d1c34dd3dab012e3eaf5b7cf5cbb",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "經濟學|27": {
      "questionId": "115-09-2-27",
      "subject": "經濟學",
      "questionNumber": 27,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "S1、S2皆為通過原點的正斜率直線；E、F屬S1；G、H屬S2；縱軸P、橫軸Q",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "Es＝(dQ/dP)×(P/Q)",
          "why": "點彈性比較數量與價格的相對變化，與曲線是否通過原點有關。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "通過原點的直線供給：P＝kQ，k＞0",
          "why": "價格與數量成正比，k表示圖上正斜率。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "將式子改寫：Q＝P/k",
          "why": "彈性公式需要數量對價格的變動率。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "dQ/dP＝1/k",
          "why": "Q對P求導得到固定斜率倒數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "P/Q＝k",
          "why": "由P=kQ，非原點正數處兩側除Q可得。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "Es＝(1/k)×k＝1",
          "why": "無論是S1或S2，也不論點在哪，彈性都為1。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "Es(E)=Es(F)=Es(G)=Es(H)=1 ⇒ A",
          "why": "四點皆單位彈性，因此E與G相等。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "四點供給彈性均為1，選A；單位：無單位（彈性係數）；選項：A",
          "why": "誤把斜率陡峭程度或點的高度直接當彈性；忽略直線過原點的特性。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "3c13bf5dc3ed5f81b7d8c0e667f5596f5a169ead9df78360ae82451e8a1e79c4",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "經濟學|28": {
      "questionId": "115-09-2-28",
      "subject": "經濟學",
      "questionNumber": 28,
      "answerCandidate": "A",
      "aiAnswer": "D",
      "needsReview": true,
      "reviewReason": "題幹未列預算但候選解以等邊際效用／價格相等認定A；未設預算下D總效用較高。需官方及教材檢視。",
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "蛋餅價格40元，總效用20、24、25、23；豆沙包價格50元，總效用5、7、8、8；三明治價格60元，總效用15、21、18、12；原題未給總預算金額",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "MU_n＝TU_n−TU_(n−1)；等邊際原則 MU蛋餅/40＝MU豆沙包/50＝MU三明治/60（通常需預算約束）",
          "why": "將總效用換成邊際效用，比較每元效用；同時檢查缺少預算約束時的總效用。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "蛋餅 MU1=20，MU2=24−20=4，MU3=25−24=1，MU4=23−25=−2",
          "why": "同商品每增加一份的效用。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "豆沙包 MU1=5，MU2=7−5=2，MU3=8−7=1，MU4=8−8=0",
          "why": "先算出各單位的新增效用。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "三明治 MU1=15，MU2=21−15=6，MU3=18−21=−3，MU4=12−18=−6",
          "why": "第3份之後效用變低。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "A(2,1,2)：4/40＝5/50＝6/60＝0.10",
          "why": "候選A滿足等邊際效用／價格比例相等，符合常見消費均衡題意。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "A花費2×40+1×50+2×60＝250元；TU=24+5+21=50",
          "why": "檢查A的總花費和總效用，但250元並非題目提供預算，不可當成已知。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "D(3,3,2)：TU=25+8+21=54；花費3×40+3×50+2×60=390元",
          "why": "若無預算上限，D在表列數量中各商品TU均為最大或不降低，總TU54高於A50。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "D最後MU/P＝1/40=0.025、1/50=0.02、6/60=0.10",
          "why": "D不是等邊際比例相等；因此兩種答案分歧源於是否預設受限預算與均衡原則。",
          "kind": "formula"
        },
        {
          "title": "比較不同推導並等待核對",
          "content": "原圖初解D（無預算TU最大54）；候選A（每元MU比率均0.10）有教科書均衡解釋，待官方／教材核對；單位：效用單位（題幹未定義）／新臺幣元；選項：UNRESOLVED_D_VS_A",
          "why": "未說明預算就把『MU/P相等』當全域最大；或只找個別總效用峰值卻忽略題目『考慮價格』的命題暗示。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "914f28cf23ad62958e9a70e85b6e1cd27bf6b9f9b04849ec8b6f84fe99d6dbef",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "經濟學|25": {
      "questionId": "115-09-2-25",
      "subject": "經濟學",
      "questionNumber": 25,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "只能四選一；喜好順序③>①>②>④；最後選①郵輪；問機會成本",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "決策的隱含代價用主觀價值較高的放棄用途衡量；不是只看金錢。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "**機會成本**不是把全部放棄方案加起來，而是選擇方案時**放棄的最佳替代選項**。",
          "why": "只能選一個活動，雖然他最想打工③，但最後去郵輪①。他因此失去的最好機會就是打工，所以③是機會成本。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "林生偏好排名③>①>②>④，但最後選①郵輪，因此放棄選項中的最高偏好是③**飲料店打工**，選C。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "雖③有最低工資與福利，題目沒有數字，不能憑空算成金額。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "C打工③是林生偏好第一名，卻因選郵輪而放棄，所以是最佳替代方案，也就是機會成本。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "ec7abde20dc64ede40c066a1b20483db3b320479b5480a778e7495366d261a34",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "經濟學|29": {
      "questionId": "115-09-2-29",
      "subject": "經濟學",
      "questionNumber": 29,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "至少一種關鍵生產投入；投入量三年內無法變動；持續生產；問長短期",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "不同產業資本設備調整速度不同，短期可能是幾週或幾年，依題目約束。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "經濟學**短期／長期**不是固定用某個年數定義，而是看**至少一種投入是否仍固定**。",
          "why": "如果工廠有一種大機器三年內不能換，這三年裡總有東西動不了，就叫短期。長期是很多事情都能慢慢調整，不是規定一定要一年或兩年。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "題目特別指定某關鍵投入在三年內無法改變，故三年內屬短期，選A。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "**長期**則指所有投入都能調整； 不可以直接把長期說成一年或兩年內。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "A指出三年以內是短期；因題目說至少一項要素三年內固定，符合短期定義，是正解。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "1ff70b0b7724f499ffe88fa9e37e624909ff0f6a61f7468a1beccac216606a06",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|2": {
      "questionId": "115-09-2-02",
      "subject": "會計學",
      "questionNumber": 2,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "A-D四選項或①②③④逐項判斷；正確表述由會計概念及原圖文字決定",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "**憑證**記錄發生交易的證據；**帳簿**系統地記錄分錄；**財務報表**彙整財務狀況與績效。保存起算點按條文是**年度決算程序辦理終了後**。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "《商業會計法》第**38條**區分兩類：**會計憑證原則上至少五年**（不計依法永久保存或未結事項等例外）；",
          "why": "發票和記帳傳票是憑證，通常至少留五年；記帳的本子和最後做出的財務報表，要至少留十年，所以選後面四項。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "**會計帳簿及財務報表至少十年**（條文另有未結事項例外）。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "①發票、②傳票屬會計憑證； ③日記簿、④分類帳屬帳簿； ⑤資產負債表、⑥綜合損益表屬財務報表。 故十年是**③④⑤⑥，選D**。 法源已由經濟部主管法規及全國法規資料庫第38條獨立核查； 但未直接比對考試最終答案PDF。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "③日記簿、④分類帳為帳簿；⑤資產負債表、⑥綜合損益表為財務報表，法定一般期間至少十年，選D。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "f3b847cf2d16a4e217ecbdf6d6af3b0daeb48a817804e415c1e24d84815670bf",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|3": {
      "questionId": "115-09-2-03",
      "subject": "會計學",
      "questionNumber": 3,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "A-D四選項或①②③④逐項判斷；正確表述由會計概念及原圖文字決定",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "存貨是為正常營業過程出售而持有的資產；固定資產與存貨分類要看**持有目的**。進貨運費是使存貨達到當前地點與狀態的成本。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "本題正解是 **C：汽車經銷商購入汽車『以供出售』，屬正常營業過程中待售商品，應認列存貨**。",
          "why": "車行買進來是**要賣給客人**的汽車，所以算店裡等待賣出的貨。買商品時把它運進倉庫的錢，通常也要算在這批貨的成本裡。題目不是說車行要把車拿去出租。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "A支付員工薪資涉及對外的員工，非內部帳務調整；",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "B地震損失是非交易性資產損失，不能直接當作與外部對象交換的對外交易； D為使購入商品達到目前地點與狀態所需的進貨運費，通常納入**存貨成本**，而非立即作一般營業費用。 重要：本輪初看原圖曾將『出售』誤看成『出租』而推測 B，查候選後重新逐字目視確認原圖是『出售』，才改為 C； 不冒稱初次盲解正確，仍需獨立複核。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "**汽車經銷商買汽車以供出售**，目的就是待售商品，符合存貨定義。原圖明確為『出售』而非『出租』，故正確。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "16e5634a17680ca04fc76d82f72ef1e76c423aa5e5ed80062c0cec63b7c05163",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|4": {
      "questionId": "115-09-2-04",
      "subject": "會計學",
      "questionNumber": 4,
      "answerCandidate": "B",
      "aiAnswer": "B",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "A-D四選項或①②③④逐項判斷；正確表述由會計概念及原圖文字決定",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "**分錄**先記交易；**過帳**把日記簿中的金額按科目轉到分類帳，並用相互頁碼方便追查來源。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "日記簿有供填分類帳頁數的**類頁**欄；",
          "why": "一本先記每天發生的事（日記簿），另一本照會計科目整理（分類帳）。互相記『在哪一頁』，但日記簿的欄叫類頁、分類帳的欄叫日頁。第二句說對。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "分類帳有供填日記簿頁數的**日頁**欄。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "分錄時通常先記日期、科目、金額； 完成**過帳**後在**分類帳的日頁欄寫日記簿頁碼**，同時在**日記簿的類頁欄寫分類帳頁碼**。 所以只有②正確，選B。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "②把日記簿頁碼記到分類帳**日頁**欄，是過帳互相索引的正確方式；①③不正確。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "3b1493b56ac9296369fdbdf8771bf20dcfb86b90b74810324ad6ec22aba9123d",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|5": {
      "questionId": "115-09-2-05",
      "subject": "會計學",
      "questionNumber": 5,
      "answerCandidate": "B",
      "aiAnswer": "B",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "A-D四選項或①②③④逐項判斷；正確表述由會計概念及原圖文字決定",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "**實帳戶**是資產、負債、權益；**虛帳戶**是收益與費損。**權責發生基礎**按發生期間認列收入費用而非僅按現金進出。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "①錯：預付若起初記資產（記實轉虛），期末**借費用（虛）貸預付資產（實）**；",
          "why": "預付像先付下一季房租，有時先記成資產、有時先記成費用，所以調整的借方不一定都一樣。應付是已花但還沒付，借費用；應收是已賺但還沒收，漏記會少算收入。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "若起初記費用（記虛轉實），才可能借預付（實），所以非一定借實。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "②對：應計應付費用應**借費用（虛）、貸應付（實）**。 ③錯：預收起初記收益（虛），漏做調整會使應轉負債的部分**收入與淨利高估**，不是低估。 ④對：應收收入漏調會使應認列收入未入帳，**淨利低估**。 故②④正確，選B。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "②應付調整借費用虛帳，④應收調整漏做使收益／淨利低估，兩句皆對；選B。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "85e6398a3252c22a11455b5b7647d035ef6cd0bffe1887a4cf1010c58ec4e6aa",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|6": {
      "questionId": "115-09-2-06",
      "subject": "會計學",
      "questionNumber": 6,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": true,
      "reviewReason": "初解B後才讀候選D並發現漏掉上一年末結轉；修正D但須獨立複核。",
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "X1、X2年末應收帳款借餘500000與600000；排除信用損失率為零，問X2年初、年度中、期末調整後的備抵損失餘額方向。",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "備抵損失為應收帳款抵銷科目；核銷借記備抵、估列貸記備抵。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "①正確：X1年終調整後的備抵貸餘承接至X2年初。",
          "why": "去年年底預留了可能收不回的款項，新年一開始會沿用。中間可能用掉一些，到年終再重新計算。第一句和第三句對。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "②錯：年度中若核銷壞帳，備抵可變借餘。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "③正確：X2期末重新依非零預期信用損失率調整後應為貸餘。 因此①③、選D。 首次只想到年度中不一定貸餘而漏掉上年底餘額結轉，初解B，候選提示後改D，須獨立複核。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "對照候選及待查疑點",
          "content": "初解B後才讀候選D並發現漏掉上一年末結轉；修正D但須獨立複核。",
          "why": "本題待官方答案與教材獨立查核。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "260ff739935f3ac116b51e4b81f3c0397c4dfcb142e50a60002a4861fca2c900",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "商業概論|1": {
      "questionId": "115-09-1-01",
      "subject": "商業概論",
      "questionNumber": 1,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "①講座屬法定義務？；②自主減碳是否承擔社會責任？；③成本提升與倫理責任？；④股東利潤受損與經濟責任？",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "經濟、法律、倫理與慈善責任是不同層次；現實CSR不能僅憑一次利潤變動定論。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "辨別CSR的**經濟、法律、倫理、慈善**層次。",
          "why": "公司要守法律、努力賺錢、也要顧地球。主動用乾淨能源是好的；辦講座不等於法律硬規定。少賺錢會影響股東，卻不能說只要少賺一次就一定不負責任。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "①自願辦社區講座並不等於履行法律強制義務；",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "②再生能源減碳是環境與社會責任； ③營運成本上升首先關乎**經濟**面，而非最基本**倫理**責任。 若沿用本考題將維護股東獲利列為經濟責任的簡化分類，④會被視為經濟面，因此候選答案D（②④）； 但『利潤受損**即**未善盡』推論過強，仍須官方命題解釋。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "D為②④；依命題的責任層次分類，②屬社會責任、④與股東獲利的經濟責任相關，故與候選D一致；但『即未善盡』需要保留語義疑點。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "da86b958242f46bb5c8cfce60a0bf9b79a72d33f3bb049c1ac801be9109ff799",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "商業概論|3": {
      "questionId": "115-09-1-03",
      "subject": "商業概論",
      "questionNumber": 3,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "個人化營養諮詢SOHO；新創博覽會和創業者交流；高齡化產生保健需求；競爭者推出類似服務",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "Mintzberg聯絡者屬人際角色；SOHO按業務分型；競爭風險需依市場資料判斷。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "SOHO工作型態要按**提供的服務類型**分類，好食光是營養諮詢，不是資訊SOHO。",
          "why": "這個小工作室教客人如何吃得健康，不是做電腦程式。小華在展覽和其他老闆聊天、交朋友，像公司對外聯絡的人。別家推出一樣的服務可能搶生意，但也要看整個市場有沒有變大。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "新創博覽會與其他創業者交流與建立聯繫符合Mintzberg管理**人際關係角色中的聯絡者**，所以候選C有明確依據。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "高齡化是人口社會變遷，不是災害。 D『類似服務出現增加經營風險』在競爭分析中**可能**成立，因此不能草率說D完全沒道理； 需核對命題定義與官方說明。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "C指出小華跟外部創業者交流、維繫聯繫，符合管理者的人際**聯絡者**角色，為候選正解。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "b0720a8d88dabeaba5e8dc9450bf14eef27de3f45dc6a4459465047d8bdca55a",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "商業概論|5": {
      "questionId": "115-09-1-05",
      "subject": "商業概論",
      "questionNumber": 5,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "①人力銀行求職媒合；②電子書下載購買；③影音平台付費觀看比賽影片；④網路訂機票與飯店住宿",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "數位化商品著重內容本身；線上服務提供搜尋、媒合、預訂；依課程主要交易標的分類。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "判斷電子商務**數位化商品**與**線上服務商品**，不要只看交易在網路發生。",
          "why": "花錢讀電子書、看線上影片，是拿到手機裡的內容；用求職網站、訂飯店網站，是請網站幫忙找機會或訂服務。因此③和④這一組配對對。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "②電子書與③付費影音主要交付數位內容；",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "①人力銀行做媒合、④訂票訂房做預約交易，主要屬線上服務。 D把③列數位化商品、④列線上服務，符合此考題分類； 部分串流商業模式也兼具服務性，這是課程分類界線而非普世法規。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "D把③付費影片列數位化商品，④機票飯店網路訂購列線上服務，兩者均符合命題分類。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "96ab298a88b9f98416b91d3935ef3e64723ab5b7d1fd55928d1412ac6b14ff3c",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "商業概論|6": {
      "questionId": "115-09-1-06",
      "subject": "商業概論",
      "questionNumber": 6,
      "answerCandidate": "B",
      "aiAnswer": "B",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "①持票兌換50元優惠券；②網紅拍影片在社群宣傳；③打卡抽獎送禮；④餐酒館特調並付費雜誌宣傳",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "促銷組合包括廣告、銷售推廣、公共關係、人員推銷、直接行銷等；本題以活動的主要手段判斷。即便整場活動可同時運用多種工具，**銷售推廣**的辨識重點仍是短期誘因。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "銷售推廣是短期給予消費者誘因以刺激購買或參與。",
          "why": "優惠券能少付50元、抽獎有機會拿禮物，這些都像『來參加就有好康』。拍宣傳影片、付錢登雜誌廣告，是告訴大家消息，不一定給參加者好處，所以選①和③。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "①憑門票領50元優惠券屬折價券促銷，③打卡抽獎送好禮屬抽獎促銷；",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "②網紅影片宣傳屬廣告／公關傳播，④付費雜誌宣傳屬廣告。 故①③，B。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "B 選①③；①優惠券帶來價格誘因，③打卡抽獎送禮帶來中獎誘因，皆能短期鼓勵歌迷參與與消費，因此這組正確。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "5e79e4e8730a1cce0358c9e5321db8fbdfe373b85e8aa8a2ad6ed32073ea8801",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "商業概論|7": {
      "questionId": "115-09-1-07",
      "subject": "商業概論",
      "questionNumber": 7,
      "answerCandidate": "B",
      "aiAnswer": "UNDETERMINED",
      "needsReview": true,
      "reviewReason": "候選B與廣義財務槓桿理論相衝突；TEJ財務槓桿文件提及特別股固定財務成本，需官方115年最終解答／更正及教材定義複核。",
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "票據貼現的籌資期限；特別股是否可能產生財務槓桿；公司債相對特別股發行成本；公司債利息稅盾",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "財務槓桿狹義用舉債衡量，廣義可考慮具有固定股利的特別股對普通股盈餘的放大效果；此題候選解答與較廣義解釋存在定義歧義。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "A票據貼現通常屬**短期融資**；",
          "why": "票據貼現是把快到期的票換成現金，不是長期借錢。公司債付的利息通常可能節稅。特別股優先分股利，有時也會放大普通股東剩下的獲利起伏，所以說它『完全不可能有槓桿』有問題。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "C債券資金成本通常並不必然高於特別股；",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "D符合規定的公司債利息一般可稅前扣除，存在**節稅效果**。 候選B斷言**特別股無法發揮財務槓桿**，但財務理論中固定特別股股利可能使普通股EPS對EBIT變動更加敏感，廣義財務槓桿可包含此效果。 某些高職課本可能將『舉債』當槓桿狹義定義； 未確定教材與官方更正前不能說B在所有定義下正確。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "對照候選及待查疑點",
          "content": "候選B與廣義財務槓桿理論相衝突；TEJ財務槓桿文件提及特別股固定財務成本，需官方115年最終解答／更正及教材定義複核。",
          "why": "本題待官方答案與教材獨立查核。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "07507836cc787e0535eb3e237d8f61a0f5c3dd7edf1674d7c72bb583f6bb340d",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數位科技|26": {
      "questionId": "115-09-1-26",
      "subject": "數位科技",
      "questionNumber": 26,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "題問錯誤；Big-5 / Unicode / ASCII / 二進位",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "字元編碼、Unicode碼位與UTF格式不可混同；ASCII原始7位元，常見儲存一byte。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "Big-5是面向繁體中文字形與字元的傳統編碼，並不是『常用英文編碼系統』；",
          "why": "打英文和打繁體中文，需要用電腦看得懂的字元編號。Big-5比較像繁體中文字典，不是英文專用字典，所以A錯。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "Unicode通稱萬國碼；",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "標準ASCII編碼核心7位元，常存放於8位元byte中，題幹的『可由8位元所組成』在儲存語境可成立； 編碼將字元映射至電腦可處理的碼值。 故最錯的是A。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "**A錯**。Big-5用於繁體中文漢字等字元編碼，不能稱作常用英文編碼系統；此選項符合題問『錯誤』。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "1121850558b92aeb994fa355456b31dc0ae03cc7e087458b78de6e58741338fb",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數位科技|27": {
      "questionId": "115-09-1-27",
      "subject": "數位科技",
      "questionNumber": 27,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "以Linux系統開發新產品；自由軟體／共享軟體／公用軟體／免費軟體",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "free speech 而非 free beer 是常用比喻；GPL、MIT、Apache 等授權規則各不同；實際能否販售和是否需提供原始碼要看授權。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "Linux核心等常見開源授權允許在符合授權條件下商業銷售，自由軟體的『自由』不等於『必須免費』。",
          "why": "有人把開源程式改好拿去賣，是可以的，但要遵守原本規定。『自由使用修改』不代表『一律不能收錢』；『免費』也不代表大家可以隨便拿去改。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "共享軟體可有期限和付費限制，免費軟體仍通常有著作權。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "故A。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "A符合自由軟體可商業銷售的原則，但再散布時應遵守適用的開放原始碼授權義務，不能因此說毫無條件。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "a3b18d6faabb4321b1fc3bec4592f136190ce831432bccc7ab4ee13f5f4ffce8",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數位科技|28": {
      "questionId": "115-09-1-28",
      "subject": "數位科技",
      "questionNumber": 28,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "串列傳輸；全雙工＝同時傳送接收；PS/2 / VGA / HDMI / 網卡接交換器",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "單工只單向、半雙工雙向輪流、全雙工雙向同時；物理連接和設備協商設定也影響實際是否全雙工。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "網路卡與交換器一般協商為全雙工乙太網路，同一時間可以傳送與接收；",
          "why": "像兩個人都能同時說話也都能聽見，叫全雙工。電腦用網路線接交換器，可以邊送資料邊收資料，所以選D。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "資訊經鏈路以串列方式傳輸。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "PS/2雖是串列卻不是典型全雙工； VGA是類比視訊非典型串列； HDMI視訊傳輸主要單向。 因此D。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "D網卡接交換器在一般可支援且協商為全雙工的乙太網路連線，可同時傳送與接收資料，符合串列＋全雙工。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "406eaa84ccc681598d20d6e2bdbb1726c97ee9cf5b6b44f2418a85cccc702487",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數位科技|32": {
      "questionId": "115-09-1-32",
      "subject": "數位科技",
      "questionNumber": 32,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "家庭旅行共同排程；手機平板筆電同步查看和編輯；最方便且即時",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "即時協作和『傳送檔案給別人』不同；權限要給需要編輯者，而非全部公開。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "雲端硬碟共享行程文件、設定編輯權限後，一份行程能由家人在多裝置存取編輯；",
          "why": "全家要一起改旅遊計畫，就把同一份檔案放雲端、給大家可以編輯的連結。不用每個人一直傳照片，不會搞不清楚哪份最新版。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "電郵、相簿圖片、藍牙檔案傳輸不能讓大家像共用檔案般即時協作。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "因此C。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "C上傳雲端並設定權限共享連結，可由手機、平板、筆電看同份檔案與共同修改，最符合需求。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "5fc53d27531c283f829e7e3e76c453d16615b8e82657c39ffc1ecbb66725c850",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數位科技|34": {
      "questionId": "115-09-1-34",
      "subject": "數位科技",
      "questionNumber": 34,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "題問錯誤；NFC 行動支付；eTag與RFID；RFID Tag耗電量；4G LTE與ZigBee距離",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "物聯網通訊比較要辨別距離、能耗、資料率、被動與主動標籤；不能將所有RFID標籤視為電池設備。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "NFC可用於感應行動支付，eTag是RFID技術應用；",
          "why": "eTag過高速公路會感應、手機靠近也能付款。RFID小標籤有的根本不用裝電池，靠旁邊讀取機的訊號就能工作，所以不能說每種都很耗電。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "4G LTE常見蜂巢網路覆蓋距離比近距離ZigBee長。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "被動式RFID Tag不需要電池，靠讀取器電磁場取能，不可一概說Tag耗電量大，故C。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "C錯在『Tag耗電量大』過度概括。被動式RFID Tag常無電池、取能於讀取器，不能一律說耗電量大，因此本題選C。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "e4b9be479dda5b2ed41563bbf944eedc1d1ea1086ecde8691af24ebe5aa359b6",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|1": {
      "questionId": "115-00-MB-01",
      "subject": "數學 B",
      "questionNumber": 1,
      "answerCandidate": "B",
      "aiAnswer": "B",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "圖格原點 O=(0,0)、S=(0,2)、T=(3,0)；A=(3,2)、B=(−3,2)、C=(−3,−2)、D=(3,−2)",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "向量 PQ=(xQ−xP, yQ−yP)；向量相減 (u₁,u₂)−(v₁,v₂)=(u₁−v₁,u₂−v₂)",
          "why": "向量加減可描述平面上的位移，物流或地圖中用來表示從 A 點移動至 B 點的方向與距離。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "OS=S−O=(0−0,2−0)=(0,2)",
          "why": "向量從 O 指到 S，以終點減起點。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "OT=T−O=(3−0,0−0)=(3,0)",
          "why": "向量從 O 指到 T，同樣取座標差。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "OS−OT=(0,2)−(3,0)=(0−3,2−0)=(−3,2)",
          "why": "向量相減，x、y 分量分別相減。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "OB=B−O=(−3−0,2−0)=(−3,2)",
          "why": "圖上 B 的坐標和計算結果相同，因此就是 OB。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "(−3,2)；單位：座標單位（格）；選項：B",
          "why": "把減法順序倒成 OT−OS 得到 (3,−2)，誤選 D；或只比較向量長度。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "5735eef691797736d38a82597852739a9d122e11064e36c896afd18dbb011be7",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|2": {
      "questionId": "115-00-MB-02",
      "subject": "數學 B",
      "questionNumber": 2,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "α≠β，故 α−β≠0；r₁=α+β，r₂=α−β；方程式 x²−8x+5(α−β)=0",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "若 x²+bx+c=0 根為 r₁,r₂，則 r₁+r₂=−b、r₁r₂=c（韋達定理）",
          "why": "韋達定理不用解出每個根，也能從二次式得到根的和與積。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "(α+β)+(α−β)=−(−8)=8",
          "why": "兩根相加等於 x 項係數相反數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "2α=8 ⇒ α=4",
          "why": "左右 β 抵消，只剩 2α。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "(α+β)(α−β)=5(α−β)",
          "why": "兩根相乘等於常數項。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "α−β≠0 ⇒ α+β=5",
          "why": "因題目給 α≠β，可合法將兩側同除 α−β。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "β=5−α=5−4=1",
          "why": "由根積關係求 β。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "αβ=4×1=4",
          "why": "題目要的是 α 與 β 的乘積而非根和。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "4；單位：無單位；選項：A",
          "why": "未核對 α≠β 就約分；或把 α+β=5 誤作 αβ。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "c159f4f02a503c998f57213d73f6069acdeaf6ab521aca1cc9719a04a83e8a1d",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|3": {
      "questionId": "115-00-MB-03",
      "subject": "數學 B",
      "questionNumber": 3,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "L₁:2x+3y=4；L₂∥L₁；a=L₁的x截距，m=L₂斜率",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "x 截距令 y=0；Ax+By=C ⇒ y=−(A/B)x+C/B，斜率 m=−A/B；平行直線斜率相等",
          "why": "從一般式求斜率與截距，快速比較兩條直線方向。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "令 y=0：2a+3(0)=4 ⇒ 2a=4 ⇒ a=2",
          "why": "x 軸上的所有點 y=0，與該軸交點之 x 就是截距。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "2x+3y=4 ⇒ 3y=−2x+4 ⇒ y=−(2/3)x+4/3",
          "why": "改寫成 y=mx+b 才能讀出 x 的係數為斜率。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "m₁=−2/3；L₂∥L₁ ⇒ m=m₁=−2/3",
          "why": "互相平行的非垂直直線斜率相同。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "(a,m)=(2,−2/3)",
          "why": "把剛算到的 x 截距和 L₂ 斜率依題目要求排序。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "(2, −2/3)；單位：截距為座標單位；斜率無單位；選項：A",
          "why": "把 y 截距 4/3 當 x 截距；或漏掉 − 號。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "03d5f494eb30b1fc452586e5bf1d1de5a917ba2cc98291e8bace8273b8a6872b",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|4": {
      "questionId": "115-00-MB-04",
      "subject": "數學 B",
      "questionNumber": 4,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "2x²+7x+3≤0；解表示為 a≤x≤b",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "因式分解 (2x+1)(x+3)≤0；二次式係數為正時，乘積≤0 在兩個根之間（含端點）",
          "why": "找出二次不等式成立的變數區間，亦可用符號表驗算。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "2x²+7x+3=(2x+1)(x+3)",
          "why": "展開為2x²+6x+x+3=2x²+7x+3，分解正確。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "2x+1=0 ⇒ x=−1/2；x+3=0 ⇒ x=−3",
          "why": "讓兩個因式分別等於零，求臨界點。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "−3 < −1/2；又二次項係數 2>0",
          "why": "排列根的先後，判斷圖形開口向上。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "(2x+1)(x+3)≤0 ⇒ −3≤x≤−1/2",
          "why": "兩根之間異號，乘積非正；因等號也允許，包含兩端。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "a=−3∈ℤ，b=−1/2∉ℤ ⇒ 選 C",
          "why": "比較四選項需確認 a、b 的整數性與大小。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "a=−3，b=−1/2；選 C；單位：實數區間，無單位；選項：C",
          "why": "忘了含端點、負數大小比較顛倒、將 −1/2 誤判整數。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "0fa2c98cf699f4d4dab11680416d812efcad34eaf9faf6ed5f7de8030ec17562",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|5": {
      "questionId": "115-00-MB-05",
      "subject": "數學 B",
      "questionNumber": 5,
      "answerCandidate": "B",
      "aiAnswer": "B",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "A=(−1,0)；B=(0,−5)；D=(2,3)；ABCD 為依序平行四邊形",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "對邊向量 BC=AD=D−A；C=B+(D−A)；中點 M=((xB+xC)/2,(yB+yC)/2)",
          "why": "中點公式求兩座標點正中央的位置；平行四邊形利用等向量求未知頂點。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "AD=D−A=(2−(−1),3−0)=(3,3)",
          "why": "平行四邊形對邊向量相同，先求從 A 到 D 的位移。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "BC=AD=(3,3)",
          "why": "依 A→B→C→D 順序，BC 與 AD 是方向與大小相同的對邊。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "C=B+BC=(0,−5)+(3,3)=(3,−2)",
          "why": "由 B 位移(3,3)可以到 C，得到未知頂點。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "Mx=(xB+xC)/2=(0+3)/2=3/2",
          "why": "取線段兩端的水平座標平均。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "My=(yB+yC)/2=(−5+(−2))/2=−7/2",
          "why": "取垂直座標平均，負負相加得−7。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "M=(3/2,−7/2)，選 B",
          "why": "中點座標對應選項 B。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "(3/2,−7/2)；單位：座標單位；選項：B",
          "why": "把 B_y=−5、C_y=−2 的平均算成−5/2，或將 C 的 x 值求錯。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "be5bb1f0e23eddff9e8a0f17e6e116ce2ce4219205f4527d50a710fb76e20dd2",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|6": {
      "questionId": "115-00-MB-06",
      "subject": "數學 B",
      "questionNumber": 6,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "f(x)=x⁴−3x³+2x²−x+1；除式 g(x)=(x−1)(x−2)",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "f(x)=g(x)Q(x)+R(x)，deg R<deg g=2 ⇒ R=mx+n；R(1)=f(1)、R(2)=f(2)",
          "why": "用餘式定理與一次式待定係數，比長除法更快找二次除式的餘式。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "g(1)=0、g(2)=0，令 R(x)=mx+n",
          "why": "除式在1與2為零，代入除法恆等式可消去 g(x)Q(x)。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "f(1)=1−3+2−1+1=0 ⇒ m+n=0",
          "why": "算出餘式在1時的值。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "f(2)=16−24+8−2+1=−1 ⇒ 2m+n=−1",
          "why": "算出餘式在2時的值。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "(2m+n)−(m+n)=−1−0 ⇒ m=−1",
          "why": "將聯立兩式相減消去 n。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "n=−m=1 ⇒ R(x)=−x+1",
          "why": "回代求常數項，寫出完整餘式。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "R(x)=−x+1；單位：無單位；選項：D",
          "why": "只有用 x=1 檢查而未檢查 x=2；或計算 f(2) 的負號錯。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "bbf46a7b80de52c10e23cd038d33401eb199a4626554c5c1b7f98f5673bb330f",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|8": {
      "questionId": "115-00-MB-08",
      "subject": "數學 B",
      "questionNumber": 8,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "A=(0,0)；B=(4,0)；C=(−2,2√3)；θ 是 AB 與 AC 的夾角",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "向量 AB·AC=|AB|×|AC|×cosθ；內積=uxvx+uyvy；向量長度 √(x²+y²)",
          "why": "內積可求兩向量夾角，尤其題目以座標而不是直角三角形給條件時。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "AB=(4−0,0−0)=(4,0)",
          "why": "求 A 指向 B 的向量。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "AC=(−2−0,2√3−0)=(−2,2√3)",
          "why": "求 A 指向 C 的向量。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "AB·AC=4×(−2)+0×2√3=−8",
          "why": "分量相乘後相加得到內積。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "|AB|=√(4²+0²)=4",
          "why": "使用畢氏定理得 AB 長度。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "|AC|=√((−2)²+(2√3)²)=√(4+12)=4",
          "why": "先平方 √3 項，2√3 平方=12。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "cosθ=(AB·AC)/(|AB|×|AC|)=−8/(4×4)=−1/2",
          "why": "將內積除兩向量長度乘積，得到選 D。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "cosθ=−1/2；單位：餘弦值無單位；選項：D",
          "why": "錯把 (2√3)² 當作 4√3；或忽略 AB·AC 負號。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "dcad64f776b9128299839aee37597d7509d4155c01a9bc81092fd30bad96aec6",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|13": {
      "questionId": "115-00-MB-13",
      "subject": "數學 B",
      "questionNumber": 13,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "26x+15y≤2026；15x+26y≤2026；以完整四圖選擇交集",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "Ax+By≤C（B>0）⇒y≤−Ax/B+C/B；聯立取交集；代(0,0)測半平面。",
          "why": "以測試點與半平面交集處理線性不等式。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "直線①：y=−(26/15)x+2026/15，斜率−26/15，y截距約135.07",
          "why": "正係數除過去保留≤方向。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "其x截距2026/26≈77.92",
          "why": "由y=0得x截距。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "直線②：y=−(15/26)x+2026/26，斜率−15/26，y截距約77.92",
          "why": "另一邊界同法求斜率與截距。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "其x截距2026/15≈135.07",
          "why": "求第二條x截距以核對圖形。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "交點兩式相減11x−11y=0 ⇒x=y=2026/41≈49.41",
          "why": "兩線相交約在(49.41,49.41)。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "(0,0)：兩式左邊都是0，均≤2026",
          "why": "測原點是快速找陰影的一種方法。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "共同下方含原點的圖是A",
          "why": "選同時成立的陰影交集。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "A（共同下方含原點）；單位：圖形座標單位；選項：A",
          "why": "只看斜率就選C卻沒判原點是否在陰影。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "9ec74bf1b9556f189212050527a37d0310940f37788e088a522df34edaf55617",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|14": {
      "questionId": "115-00-MB-14",
      "subject": "數學 B",
      "questionNumber": 14,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "原數列公比3；x,y,z正整數；y−x=z−y=2",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "a_y/a_x=r^{y−x}，a_z/a_y=r^{z−y}，取r=3。",
          "why": "固定間隔抽取等比數列仍成等比，公比是原公比的間距次方。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "y−x=2、z−y=2",
          "why": "等差索引公差為2。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "a_y/a_x=3^{y−x}=3²=9",
          "why": "每隔兩項原比值要乘兩次3。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "a_z/a_y=3^{z−y}=3²=9",
          "why": "同理第二對亦然。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "兩比相等均9 ⇒新等比數列、公比9，選D",
          "why": "符合等比數列的相鄰比值固定。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "等比，公比9；單位：無單位；選項：D",
          "why": "把公比誤當公差；把3²−1當新公比8。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "458f014169cc2a6b35d5e71c92c83002a7d91ce4d5c22a7d0693f80ab1ac904b",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|15": {
      "questionId": "115-00-MB-15",
      "subject": "數學 B",
      "questionNumber": 15,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "T(x)=10650×32^{−0.1x}天；原35°C，新27°C",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "倍率=T(27)/T(35)，a^m/a^n=a^{m−n}。",
          "why": "以指數函數比值比較不同條件的倍率。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "T(27)=10650×32^{−2.7}天",
          "why": "把27代入指數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "T(35)=10650×32^{−3.5}天",
          "why": "把35代入指數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "T(27)/T(35)=32^{−2.7−(−3.5)}=32^{0.8}",
          "why": "比值消去10650，指數相減。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "32^{0.8}=32^{4/5}=(2⁵)^{4/5}=2⁴=16",
          "why": "將32轉換成2的次方來化簡。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "新保鮮期為原本16倍，選D",
          "why": "題問倍數，因此只回比值。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "16倍；單位：倍（T的天數被相除）；選項：D",
          "why": "將天數相減而非相除；忽略32^{−0.1x}中負指數。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "304b3844a384648e5643468c5eeaee79fb0bc0716fa168e8136a90f790841b15",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|16": {
      "questionId": "115-00-MB-16",
      "subject": "數學 B",
      "questionNumber": 16,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "2008～2016九筆：198733,191310,166886,196627,229481,199113,210383,213598,208440；圖1970～2025全年出生數折線；2017～2025表格數字 193844,181601,177767,165249,153820,138986,135571,134856,107812",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "n=9為奇數，中位數=排序後第(n+1)/2=5筆；全距=max−min。",
          "why": "排序求中位數、最大減最小求全距，並用時間序列逐點比對。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "2008～2016共有2016−2008+1=9筆資料。",
          "why": "含2008與2016兩端共有九年。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "小到大排序：166886<191310<196627<198733<199113<208440<210383<213598<229481。",
          "why": "中位數必須先排序，不能按年份原順序。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "中位數位置=(9+1)/2=5，值=199113，不是229481。",
          "why": "奇數筆取正中央一筆。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "原折線約最高430000、最低107812，全距約322188>300000，B成立。",
          "why": "全距是最大減最小，可由圖判超過30萬。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "2017～2025依表193844>181601>177767>165249>153820>138986>135571>134856>107812，D成立。",
          "why": "逐年下降須每一對相鄰年份比較。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "圖上1976、1988、2000各自皆高於相鄰兩年，A成立；因此C錯誤。",
          "why": "題問『何者錯誤』，前三項正確排除後為C。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "錯誤敘述 C；中位數=199113 人；單位：人；選項：C",
          "why": "將最大值229481誤當中位數；或未將9筆按大小排序。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "57d2c97c6cc8ce80b03c1b43d7c919f2242dae13945945b151abea9f9891c219",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|17": {
      "questionId": "115-00-MB-17",
      "subject": "數學 B",
      "questionNumber": 17,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "固定七段LED（圖示數字8）；從七段全暗中任選不重複兩段；不計順序、不考慮旋轉或翻面",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "C(7,2)=7!/(2!5!)=7×6/2=21。",
          "why": "從n個固定物件選k個且不計先後，使用組合數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "從七個位置選第一段有7種。",
          "why": "第一段任選七段之一。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "第一段已選，第二段不能重覆，剩6種。",
          "why": "限制不重複，因此選法少一。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "若計順序是7×6=42種。",
          "why": "先算有順序的數目便於處理。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "同一對位置兩種選取先後會算兩次，除以2。",
          "why": "最後的明暗配置不顧選取先後。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "C(7,2)=42/2=21，選C。",
          "why": "得到不重複的亮燈圖案數。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "21種；單位：種；選項：C",
          "why": "把次序算兩次選A 42；或錯誤乘7×2選D 14。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "8c55964cf7cec4143310da4282e1ed2c4b6e4d95c8327c3e9ef159998b4a26ab",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|18": {
      "questionId": "115-00-MB-18",
      "subject": "數學 B",
      "questionNumber": 18,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "票價50元；P(10000元)=1/1000；P(5000元)=2/1000；P(1000元)=5/1000；P(500元)=1/100；不中奖獎金為0元",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "E(獎金)=Σ獎金_i×機率_i；E(淨獲利)=E(獎金)−成本。",
          "why": "加權平均計算期望，淨收益還要扣成本。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "10000×(1/1000)=10元",
          "why": "頭獎獎金乘其發生機率。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "5000×(2/1000)=10元",
          "why": "貳獎同樣作加權。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "1000×(5/1000)=5元",
          "why": "參獎加權。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "500×(1/100)=5元",
          "why": "肆獎1%要轉成1/100。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "不中獎時獎金0元，該項對期望的貢獻=0",
          "why": "未中獎不會額外得到獎金。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "E(獎金)=10+10+5+5=30元",
          "why": "四種獎金的平均加權合計。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "E(獲利)=30−50=−20元，選C",
          "why": "固定購票成本每次都要扣除。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "−20元；單位：新臺幣元；選項：C",
          "why": "忘了票價而得到30；或把負20誤寫正20。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "3e13e20fc9728a4541162a2de8dfa141f04650bd168d641c2d9173915d632013",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|19": {
      "questionId": "115-00-MB-19",
      "subject": "數學 B",
      "questionNumber": 19,
      "answerCandidate": "B",
      "aiAnswer": "B",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "tan1847°≈1.072；tan2126°≈−0.675；tan2205°=1.000；求tan2026°最可能的選項",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "tan(θ+180°k)=tanθ；在(−90°,90°)中tan單調遞增。",
          "why": "用正切週期和單調性對大角度三角函數做近似估算。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "2026°−11×180°=46° ⇒ tan2026°=tan46°",
          "why": "利用180度週期減少大角度。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "1847°−10×180°=47° ⇒ tan47°≈1.072",
          "why": "取得較大的鄰近角度和已知值。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "2205°−12×180°=45° ⇒ tan45°=1.000",
          "why": "取得較小的鄰近角度和已知值。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "tan45°<tan46°<tan47°，故1.000<tan46°<1.072",
          "why": "正切在這個角度區間遞增。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "46°介於45°與47°中間，附近估值≈(1.000+1.072)/2=1.036（插值估計）",
          "why": "平滑函數的局部估計，非嚴格等式。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "四選項最合理為B：1.036",
          "why": "排除不在界內或符號錯的選項。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "約1.036；單位：無單位；選項：B",
          "why": "誤把tan47的值直接當tan46；未做週期化簡。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "fc3e3cc5ae4aaa06eede83901c434769acda783a97051b0379f3e90973b1a9b4",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|20": {
      "questionId": "115-00-MB-20",
      "subject": "數學 B",
      "questionNumber": 20,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "AB=100公尺；∠A=60°；∠B=75°；AC為待求距離",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "正弦定理 AC/sinB=AB/sinC；sin(α+β)=sinαcosβ+cosαsinβ。",
          "why": "知道一邊與另外兩角時，依正弦定理解三角形邊長。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "∠C=180°−60°−75°=45°",
          "why": "三角形內角和是180°。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "AC/sin75°=AB/sin45°=100/sin45°",
          "why": "以邊及其對角使用正弦定理。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "sin75°=sin(45°+30°)=sin45cos30+cos45sin30",
          "why": "75°拆成45°+30°運用和角公式。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "=(√2/2)(√3/2)+(√2/2)(1/2)=(√6+√2)/4",
          "why": "代入特殊角的正弦、餘弦值。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "sin45°=√2/2",
          "why": "取得分母確切值。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "AC=100×[(√6+√2)/4]÷(√2/2)=100×(√3+1)/2=50(√3+1)公尺，選A",
          "why": "化簡根號與分數得距離。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "50(√3+1) 公尺（約136.60公尺）；單位：公尺；選項：A",
          "why": "將對角放錯；或在sin75°和角公式中誤用減號。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|21": {
      "questionId": "115-00-MB-21",
      "subject": "數學 B",
      "questionNumber": 21,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "AB=7公里；AC=8公里；∠ACB=60°；BC=x>4公里",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "餘弦定理 AB²=AC²+BC²−2(AC)(BC)cos∠ACB",
          "why": "兩邊和一個對角已知時，用餘弦定理求另一邊長度。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "令BC=x公里，且x>4。",
          "why": "把未知距離設為x並保留限制。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "7²=8²+x²−2×8×x×cos60°",
          "why": "已知角C的對邊是AB，正確代入餘弦定理。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "49=64+x²−16x×1/2=64+x²−8x",
          "why": "cos60°=1/2並乘開。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "x²−8x+15=0=(x−3)(x−5)",
          "why": "移項後因式分解二次式。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "x=3或5；由x>4得x=5，選A",
          "why": "利用附加條件排除x=3。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "5公里；單位：公里；選項：A",
          "why": "將C角60°對錯邊；或忘記x>4而答3公里。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|22": {
      "questionId": "115-00-MB-22",
      "subject": "數學 B",
      "questionNumber": 22,
      "answerCandidate": "B",
      "aiAnswer": "B",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "5張卡片依序排列；每張2種顯示：有/無；至少一張有",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "乘法原理2⁵；補集合計數：至少一張有=全部組合−全無組合。",
          "why": "補事件枚舉二元排列的總數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "五個固定位置各2種 ⇒2×2×2×2×2=2⁵",
          "why": "每個位置獨立決定顯示。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "2⁵=32種，含所有排列",
          "why": "全部狀態的計數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "全無只有『無無無無無』1種",
          "why": "找出違反條件的唯一情況。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "至少一張有=32−1=31種，選B",
          "why": "全部扣掉違規情況得可用種數。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "31種；單位：種；選項：B",
          "why": "選32忽略全無違規；或只算恰有1張為有而誤選5。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "3bc277802613d00f5525a3de74c7591898ac5b6c70abbb1a8cfda04e577ccb55",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|23": {
      "questionId": "115-00-MB-23",
      "subject": "數學 B",
      "questionNumber": 23,
      "answerCandidate": "B",
      "aiAnswer": "B",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "行程I每人x元；同行其中一人減3000元；行程II每人(x+2000)元；同行其中一人打八折；兩行程兩人總價相同",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "總價I=2x−3000；總價II=(1+0.8)(x+2000)，兩者相等。",
          "why": "使用一次方程描述兩種費用方案、折扣和總價比較。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "I費用=x+(x−3000)=2x−3000元",
          "why": "只有一人減免，不能兩人都減3000。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "II費用=(x+2000)+0.8(x+2000)=1.8(x+2000)元",
          "why": "只有一人八折，另一人付原價。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "方程2x−3000=1.8x+3600",
          "why": "依題目兩人總費用相等列式。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "2x−1.8x=3600+3000 ⇒0.2x=6600",
          "why": "整理移項並合併同類項。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "x=6600/0.2=33000元",
          "why": "除以0.2求未知原價。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "驗算I=63000、II=63000，選B",
          "why": "兩邊代回一致。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "33000元；單位：新臺幣元；選項：B",
          "why": "把八折當成減八成，或兩個人都打折、都減免。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|24": {
      "questionId": "115-00-MB-24",
      "subject": "數學 B",
      "questionNumber": 24,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "A=110/r；B=log₁₀3 / log₁₀(1+r/100)；r=8%；C=⌈A⌉、D=⌈B⌉",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "複利三倍 (1+r/100)^t=3 ⇒ t=log3/log(1+r/100)；無條件進位⌈x⌉。",
          "why": "對數求複利到達目標倍數的年數；估算與精確計算比較。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "A=110/8=13.75",
          "why": "代入r=8求快速估算。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "C=⌈13.75⌉=14",
          "why": "14是首個不小於13.75的整數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "B=log₁₀3/log₁₀1.08=ln3/ln1.08",
          "why": "換底公式同一比值。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "1.08¹⁴≈2.937<3，1.08¹⁵≈3.172>3 ⇒14<B<15",
          "why": "連續複利倍數夾住3可判精確年數在哪個區間。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "D=⌈B⌉=15",
          "why": "向上進位成完成倍數的整年。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "D=15=14+1=C+1，選C",
          "why": "比較D與C。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "D=C+1；C=14年、D=15年；單位：年；選項：C",
          "why": "把四捨五入當無條件進位；14.27誤取14。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "c022bdc2927532ef6ddb5601d692e2f6accc943d1cc5b0041c9515334295dfeb",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數學 B|25": {
      "questionId": "115-00-MB-25",
      "subject": "數學 B",
      "questionNumber": 25,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "P=(h,7)；P到L的距離√2；與L相切的圓式 x²−8x+(y−7)²=a",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "配方 x²−8x=(x−4)²−16；圓式 (x−h)²+(y−k)²=r²；相切時r=圓心到直線距離。",
          "why": "圓方程配方、相切半徑與點線距離關係。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "x²−8x+(y−7)²=a ⇒(x−4)²−16+(y−7)²=a",
          "why": "對x配平方並維持等式。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "整理 (x−4)²+(y−7)²=a+16",
          "why": "讀出圓的中心與半徑平方。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "圓心 P=(4,7) ⇒ h=4",
          "why": "圓心和題目P一致。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "相切半徑 r=√2 ⇒ r²=(√2)²=2",
          "why": "相切的最短距離等於半徑。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "a+16=2 ⇒ a=−14",
          "why": "由半徑平方解出a。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "h+a=4−14=−10，選C",
          "why": "計算所求的h+a。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "−10；單位：無單位；選項：C",
          "why": "漏掉配方的−16；或錯把距離√2直接當半徑平方√2。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "92f1b7b313c109b8e0a5a22bbb7396306e3c9e2ad1dcd4b4195d973645733896",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數位科技|29": {
      "questionId": "115-09-1-29",
      "subject": "數位科技",
      "questionNumber": 29,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "檔案容量2 MB；傳輸期限15秒內；選項A100Kbps、B200Kbps、C1Mbps、D2Mbps",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "最低傳輸頻寬（bit/s）＝資料量（byte）×8（bit/byte）÷傳輸秒數",
          "why": "用檔案資料總位元數除以時間，求每秒至少需送多少bit；比較候選頻寬與計算門檻。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "1 B（byte）＝8 b（bit）",
          "why": "MB是百萬位元組，Mbps是每秒百萬位元；先統一單位才能比較。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "2 MB＝2×1,000,000 B＝2,000,000 B",
          "why": "先按網路速率常用十進位MB換算，題目未特別指定MiB。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "2,000,000 B×8 b/B＝16,000,000 b＝16 Mb",
          "why": "把檔案容量從byte轉成bit。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "最低速度＝16,000,000 b÷15 s≈1,066,667 b/s≈1.067 Mbps",
          "why": "15秒內要送完，必須每秒送至少約107萬bit。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "A:16Mb÷0.1Mbps＝160s；B:16Mb÷0.2Mbps＝80s",
          "why": "100Kbps與200Kbps傳得太慢。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "C:16Mb÷1Mbps＝16s；D:16Mb÷2Mbps＝8s",
          "why": "只有2Mbps能在15秒內完成。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "若用2MiB＝2×1024² B，最低需求≈1.118 Mbps，仍為D",
          "why": "不同容量慣例不影響候選答案。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "至少1.067Mbps，選D 2Mbps（理想傳輸8秒）；單位：Mbps（megabits per second）／秒；選項：D",
          "why": "MB被當成Mb，少乘8；或選1Mbps而忽略需16秒，超過15秒。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "743fd5cec07f8e87c0c21aaffd63af9eb50f419596c6be00e7fe54a75737f84b",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "數位科技|33": {
      "questionId": "115-09-1-33",
      "subject": "數位科技",
      "questionNumber": 33,
      "answerCandidate": "A",
      "aiAnswer": "UNDETERMINED",
      "needsReview": true,
      "reviewReason": "②將『密碼學雜湊、數位簽章』泛稱為『資料加解密』，技術上並不等同；候選A保留並標示 BLOCKED，待官方更正及教材定義核實。",
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "①驗證後難以竄改；②加密技術對資料加解密；③透過金資中心跨行金融交易；④只保存在買賣雙方自己的帳本",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "hash不可逆；digital signature用於簽署和驗證；encryption/decryption通常是保密通訊的可逆操作；區塊鏈不必依賴中央金融交換中心。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "①區塊鏈經驗證後的記錄有抗竄改性（實務上非數學上絕對不可能改）；",
          "why": "區塊鏈像很多人都保存同一本記帳簿，想偷偷改其中一頁很難。確認身分會用特殊數學方法，但不表示每筆交易都先上鎖、再把鎖打開才算完成；『用密碼學』不一定等於『把資料加密又解密』。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "③所稱金資中心作為所有區塊鏈交易中央節點不符典型公有鏈去中心化；",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "④只寫雙方自己的帳本與分散式共識記帳相反。 ②若廣義把密碼學工具稱作『加密技術』有課本簡化空間，但比特幣核心運用雜湊與數位簽章，交易內容並不必然經『加密後解密』才驗證，語義不嚴謹。 候選A含①②，待官方與教材確認，不可把②寫成技術必然。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "對照候選及待查疑點",
          "content": "②將『密碼學雜湊、數位簽章』泛稱為『資料加解密』，技術上並不等同；候選A保留並標示 BLOCKED，待官方更正及教材定義核實。",
          "why": "本題待官方答案與教材獨立查核。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "6c8442d1e9755a877de7e479d0f3cf26af88f5701003602274e5f7197bd7dd31",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|1": {
      "questionId": "115-09-2-01",
      "subject": "會計學",
      "questionNumber": 1,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "A-D四選項或①②③④逐項判斷；正確表述由會計概念及原圖文字決定",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "辨別**期間報表與時點報表**。資產=負債+權益是某日的財務狀況，綜合損益表反映一期間收益與費損。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "①**現金流量表**彙總特定期間的營業、投資、籌資現金流；",
          "why": "有的表像『這學期收支記錄』，是在講一段時間；但資產負債表像『今天拍一張財務照片』，只看某一天的樣子。第四句把今天說成一整段時間，所以錯。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "②**權益變動表**說明期間權益變化；",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "③**綜合損益表**描述期間經營績效； ④前半句的會計要素雖對，**資產負債表呈現特定時點**的財務狀況，並非一段期間，所以①②③正確，選C。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "①、②、③均屬期間性財務報表描述，④將時點誤作期間，因此C最完整。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "065531b2bca6a6a5fa8d6c7a2ef15722acb4f32e945badf48ebcc2be75c705b2",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|7": {
      "questionId": "115-09-2-07",
      "subject": "會計學",
      "questionNumber": 7,
      "answerCandidate": "B",
      "aiAnswer": "B",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "銷貨收入1650000、折讓50000；進貨800000、退出14000、存貨減少30000；薪資300000、折舊80000、信用減損4000；利息16000、所得稅率20%",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "淨銷貨=銷貨−折讓；銷貨成本=淨進貨+存貨減少；營業利益率=營業利益/淨銷貨×100%。",
          "why": "營業利益與稅前淨利不同，利息費用屬營業外；營業利益率分母是淨銷貨。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "淨銷貨=1650000−50000=1600000",
          "why": "銷貨折讓減少銷貨收入。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "淨進貨=800000−14000=786000",
          "why": "進貨退出抵減進貨。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "銷貨成本=786000+30000=816000",
          "why": "存貨減少代表多耗用30000的存貨。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "毛利=1600000−816000=784000",
          "why": "收入扣銷貨成本。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "營業費用=300000+80000+4000=384000",
          "why": "三項為營業費用。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "營業利益=784000−384000=400000",
          "why": "利息不屬營業費用。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "營業利益率=400000/1600000×100%=25%",
          "why": "正解為B。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "營業成本率=816000/1600000×100%=51%",
          "why": "核對A錯。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "稅前淨利=400000−16000=384000",
          "why": "扣營業外利息。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "所得稅=384000×20%=76800；稅後淨利=384000−76800=307200",
          "why": "核對C、D錯。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "營業利益率25%；單位：金額新臺幣元；比率%；選項：B",
          "why": "錯把進貨退出當銷貨折讓、將利息計入營業費用、漏扣所得稅。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "a8a0827579e919118e5cc0947db29b5a89eeb1a2a57056fddde3e09d49347fc5",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|8": {
      "questionId": "115-09-2-08",
      "subject": "會計學",
      "questionNumber": 8,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "L=A/3−250000；E=2.5L；A=L+E；E≥1.25(L+x)",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "A=L+E；E=2.5L；借款後L'=L+x，E不變。",
          "why": "資產=負債+權益；貸款買設備同時增加資產、負債，權益不立即變動。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "A=L+2.5L=3.5L",
          "why": "把權益表示成負債的倍數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "L=(3.5L)/3−250000",
          "why": "代入負債與資產比例。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "L−7L/6=−250000 ⇒−L/6=−250000 ⇒L=1500000",
          "why": "解原負債額。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "E=2.5×1500000=3750000",
          "why": "求原權益。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "L'=1500000+x，E'=3750000",
          "why": "借款購設備使負債增加。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "3750000≥1.25(1500000+x) ⇒3000000≥1500000+x",
          "why": "以權益最低比例建立不等式。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "x≤1500000，驗算3750000/3000000=1.25",
          "why": "求上限並核對，選C。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "1500000元；單位：新臺幣元；選項：C",
          "why": "把資產的三分之一讀成三分之二或把借款當成股東增資。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "2f9348b1e5a99ed36ab8d5055ec8e05deaae37ae0eaba386e3915d462149afe2",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|9": {
      "questionId": "115-09-2-09",
      "subject": "會計學",
      "questionNumber": 9,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "總銷售9000000、外銷1500000；總進項8750000、土地2250000×60%；自用車950000、員工旅遊18000與15000；前期留抵18000、稅率5%、流動比率1.5",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "銷項=國內課稅銷售×5%；可扣進項=允許扣抵交易×5%；應納=銷項−可扣進項−上期留抵；流動比率=CA/CL。",
          "why": "出口適用零稅率、土地免稅；不得扣抵自用小車與員工旅遊進項；應納不等於溢付；流動比率=流動資產/流動負債。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "國內銷售=9000000−1500000=7500000；銷項=7500000×5%=375000",
          "why": "出口按題設零稅率。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "土地=2250000×60%=1350000；房屋900000",
          "why": "土地免徵營業稅。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "不得扣抵其他=950000+18000+15000=983000",
          "why": "自用乘人小汽車及員工旅遊不得扣。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "可扣進項基礎=8750000−1350000−983000=6417000",
          "why": "排除免稅和不可扣項目。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "可扣進項=6417000×5%=320850",
          "why": "①錯誤。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "應納=375000−320850−18000=36150>0",
          "why": "本期應納而非溢付。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "期末累積留抵=0元、無本期可退溢付",
          "why": "③正確、②不成立。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "結算分錄借銷項375000；貸進項320850、留抵18000、應付36150",
          "why": "貸方三項合計375000。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "流動資產減338850、流動負債淨減338850，原CA/CL=1.5>1 ⇒比率上升",
          "why": "④正確，選D。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "D（③④）；本期應納36150元；單位：元及無單位流動比率；選項：D",
          "why": "把土地、自用車、員工旅遊當可扣進項；將應納誤當退稅。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "7f019c27728fcf07060d0d4b6bcabf02283c622a9774bb63d3cb8d5d7a790a85",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|10": {
      "questionId": "115-09-2-10",
      "subject": "會計學",
      "questionNumber": 10,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "判我國營業稅敘述何者錯誤：①進口收貨人/持有人納稅；②無銷售額免申報；③自用乘人小車不得抵進項；④只能單數月申報；⑤5-10%由立法院核定。",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "《加值型及非加值型營業稅法》第2、10、19、35條，以及申報規則的例外。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "①依營業稅法第2條正確。",
          "why": "就算公司當期沒賣東西也要依法申報；有出口的公司可申請每個月報；定實際稅率的是行政院。第二、第四、第五句才錯。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "②第35條規定一般營業人不論有無銷售額均須申報，錯。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "③第19條自用乘人小汽車不得扣抵進項，對。 ④零稅率外銷可申請按月申報，非只能單數月，錯。 ⑤第10條徵收率由行政院定之而非立法院，錯。 題目問錯的，因此②④⑤、選D。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "②、④、⑤都違反第35、10條的申報與核定規則，是全部錯誤項。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "269cc3631747d8ef14e44923a1e9eeb1163104f9daa7d8f8a0e4e06216053de8",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|11": {
      "questionId": "115-09-2-11",
      "subject": "會計學",
      "questionNumber": 11,
      "answerCandidate": "B",
      "aiAnswer": "B",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "定額零用金制度，問敘述錯誤者。",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "零用金定額制度：設立、支付、報銷、撥補、現金短溢。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "零用金可依需求增減定額，屬現金內部移轉（A）；",
          "why": "公司的小錢包花錢要留發票。這個月報帳但還沒補回錢，下個月仍可補，所以B說不行是錯的。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "由出納等專人管理零星費用（C）；",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "現金加未撥補費用憑證與定額不符，發生現金短溢（D）。 **B錯在宣稱期末僅報銷未撥補，次期不得再撥補**； 報銷費用與實際補足零用金是可跨期分離的作業。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "期末已報銷費用但未實際撥補，下期仍可補足定額；『不得再撥補』錯。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "4d26c23e9c41f7c2aeb67564834dc3a02cb36ebd20157ea7617d0d1712de2a09",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|12": {
      "questionId": "115-09-2-12",
      "subject": "會計學",
      "questionNumber": 12,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": true,
      "reviewReason": "已保留首次答案差異，後續修正不冒充獨立盲解通過。",
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "銀行存款調節表①帳與原對帳單相同無須調節、②保付支票不需調節、③公司調整分錄後帳餘等於原對帳單餘額、④在途存款需公司借記存款、⑤上月在途本月對帳單出現。",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "在途存款加銀行側；未兌現支票減銀行側；銀行手續費或利息調整公司側。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "**②⑤正確，選A**。",
          "why": "公司帳跟銀行帳即使剛好數字相同，也可能還有資料沒核對。公司月底存銀行但銀行下月才收到，應在銀行那邊調。正確的是第二、第五句。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "①錯：兩個未調餘額相同仍可能有互相抵銷未達帳。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "②保付支票銀行保證且已扣款，不列未兌現支票。 ③錯：公司調整後應與銀行**調節後正確餘額**相同，不必與**原始銀行對帳單**相同。 ④錯：在途存款已由公司記帳、銀行未入帳，要加在銀行側，不能公司重複借記。 ⑤上月在途款項進入本月對帳單通常成立。 初次解D忽略③『原對帳單』，已保留待獨立複核。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "對照候選及待查疑點",
          "content": "已保留首次答案差異，後續修正不冒充獨立盲解通過。",
          "why": "本題待官方答案與教材獨立查核。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "53fe56b7680c29c8b1da0589569f2308630b78fcaa417214c01fa7474e432cf0",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|13": {
      "questionId": "115-09-2-13",
      "subject": "會計學",
      "questionNumber": 13,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "面額50000元，不附息；發票2月1日，九個月到期；貼現率6%年率，實收49000元",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "貼現息=到期值×貼現率×貼現期間(年)。",
          "why": "不附息票據到期值=面額；貼現息=到期值×年貼現率×期間。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "到期日=2月1日+9個月=11月1日",
          "why": "依題目票據九個月到期。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "到期值=50000元",
          "why": "不附息票據不另計到期利息。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "貼現息=50000−49000=1000元",
          "why": "到期值與銀行實收差額。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "期間=1000÷(50000×0.06)=1/3年=4個月",
          "why": "用貼現公式反算時間。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "貼現日=11月1日往前4個月=7月1日",
          "why": "以到期日倒推。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "7月1日；單位：日期（貼現率為年率，金額為新臺幣元）；選項：D",
          "why": "將九個月到期算錯，或直接用實收金額做貼現公式。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "d23ae731fe5590f7235d21a163054498ffb0f9a49c8f4ab3a6b8425e7db06243",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|14": {
      "questionId": "115-09-2-14",
      "subject": "會計學",
      "questionNumber": 14,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "賒銷商品的應收帳款認列：①目的地交貨本日出貨、下月到；②分期付款本日交貨；③寄銷送交代銷商；④安裝測試重大義務尚未完成。",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "應收帳款認列依銷售是否完成與有無無條件收款權；寄銷和重大安裝有額外條件。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "①目的地交貨，雖已出貨仍未到指定地點，通常尚未完成交貨；",
          "why": "第二筆貨已交給客人，雖然客人以後才付完錢，但店家現在就能記『客人欠我錢』。另外幾筆還沒真正完成交貨或服務。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "②**已交貨**且信用良好，分期付款仍有本日收款請求權，應認列應收帳款；",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "③寄銷只是交由受託者代售，尚未實際出售； ④安裝測試是合約重要履約項目，尚未完成。 故**只有②可認列**，選A。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "只有②已交付商品且可請求餘款，應於本日認列應收帳款。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "fbac2676dbe415bd141cf10682969998065c82bdc127e4947b2469bb2b6a76d6",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|15": {
      "questionId": "115-09-2-15",
      "subject": "會計學",
      "questionNumber": 15,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": true,
      "reviewReason": "已保留首次答案差異，後續修正不冒充獨立盲解通過。",
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "200+300−20可供售件數；銷280、銷退30；實盤210、每件50元",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "可供售=期初+進貨−退貨；帳存=可供售−淨銷；盤虧=(帳存−實盤)×單位成本。",
          "why": "定期盤存由實盤決定期末數並倒算成本；永續追蹤每次進銷貨，期末需按差額調整存貨盤虧與成本。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "可供售=200+300−20=480件",
          "why": "總進貨扣進貨退出。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "淨銷售=280−30=250件",
          "why": "銷貨退回加回存貨。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "帳面期末=480−250=230件",
          "why": "永續盤存應有數量。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "實盤210<帳230 ⇒盤虧20件×50=1000元",
          "why": "非盤盈。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "定期成本=(480−210)×50=13500元",
          "why": "以實盤期末直接推銷貨成本。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "永續平時銷貨成本=250×50=12500元",
          "why": "出貨即結轉成本。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "依本題教學分類年終盤虧1000調整後成本12500+1000=13500元",
          "why": "對比①；仍需確認教材之盤虧列報政策。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "兩制期末存貨=210×50=10500元",
          "why": "期末資產按實盤數。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "①②正確、③將盤虧誤作盤盈，選C",
          "why": "與候選一致，但首次誤解已記錄。",
          "kind": "formula"
        },
        {
          "title": "比較不同推導並等待核對",
          "content": "①②正確；銷貨成本13500元、存貨10500元、盤虧1000元；單位：新臺幣元；數量件；選項：C",
          "why": "誤把盤虧當盤盈，或未處理年終盤虧調整。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "6a9840a517f22334743662035ce9553f77b5ab3e062fbfe5b66766d18b6b00fb",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|16": {
      "questionId": "115-09-2-16",
      "subject": "會計學",
      "questionNumber": 16,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "購入5000股×30元，交易手續費100元；現金股利每股2元、股票股利4%；X1末每股40元；X2出售每股50元，交易費1000元",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "X1淨利影響=股利收入+(期末FV−初始FV)−交易費；X2處分利益=出售淨價款−期初帳面金額。",
          "why": "FVTPL公允價值變動列損益；股票股利增加股數但非現金收入；出售淨價款減上期帳面價值才是當期處分損益。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "初始金融資產=5000×30=150000元",
          "why": "FVTPL交易手續費100於X1費用化。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "現金股利=5000×2=10000元",
          "why": "領現金股利產生X1收入。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "股票股利=5000×4%=200股；新股數=5200股",
          "why": "股票股利不產生X1現金收入。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X1末公允價值=5200×40=208000元",
          "why": "依期末股數乘公允價值。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X1評價利益=208000−150000=58000元",
          "why": "FVTPL公允價值差入損益。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X1淨利影響=10000+58000−100=67900元",
          "why": "加股利與評價收益，扣交易費。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X2出售實收=5200×50−1000=259000元",
          "why": "扣出售費用及交易稅。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X2處分利益=259000−208000=51000元",
          "why": "避免再扣原始150000形成跨期重覆認列。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "(67900,51000)對應D",
          "why": "按題目X1、X2順序填答。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "D：X1 67900元、X2 51000元；單位：新臺幣元；選項：D",
          "why": "把股票股利4%當現金股利，或用原始成本而非上年底公允價值作X2出售成本。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "bc4400fc6ce199f814e1811a2d4e3c211f34c83a908657b4af38144cc7d4ae0b",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|17": {
      "questionId": "115-09-2-17",
      "subject": "會計學",
      "questionNumber": 17,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "不動產、廠房及設備取得成本敘述何者正確：附條件政府贈地、自建廠房超可回收金額、拆舊屋改建、購入機器現金折扣。",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "固定資產取得成本以必要支出和現金等值價為基礎；政府補助、自建資產減損、汰舊換新需分別依準則處理。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "**D正確**：外購機器設備以**購價扣最大現金折扣後之淨額**作取得成本，未利用現金折扣依題目商科教材通常作營業外支出。",
          "why": "買機器如果有最高現金折扣，成本應按扣掉折扣的價錢記。自己蓋廠房不是越花越多就能說賺錢；拆舊房和政府送地也有另外的會計規則。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "A附條件政府補助需按是否具有合理保證及適用準則認列，不能一律延至條件完成時按當時市價入帳。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "B成本高於可回收金額，應考慮減損，不可能照成本認列自建資產利益。 C已有舊屋要先按資產除列處理，不能一律認定拆除支出必屬新屋成本、不得認舊屋處分損益。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "外購機器按可取得最大現金折扣後淨額計成本，放棄折扣另列費用，符合本題原則。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "189634b5ecbefed9e5b253bb66c380ca4cfe8079e8b2bf024bcd8fabb8bcd370",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|18": {
      "questionId": "115-09-2-18",
      "subject": "會計學",
      "questionNumber": 18,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "成本500000、原殘值5000、耐用5年；前兩年X1與X2直線法；X3年初改估剩2年、殘值2000，改年數合計法",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "直線折舊=(成本−殘值)/年限；年數合計=剩餘年數總和；剩餘基礎×剩餘年數/年數合計。",
          "why": "會計估計變動使用未來適用法，未來折舊以現有帳面減新殘值、按剩餘年限計，不追溯改前兩年折舊。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "原年折舊=(500000−5000)/5=99000元",
          "why": "用直線法算X1與X2。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "兩年累計折舊=99000×2=198000元",
          "why": "計入已使用兩年度。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X3初帳面=500000−198000=302000元",
          "why": "從原成本扣累折。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "新可折舊基礎=302000−2000=300000元",
          "why": "依剩餘估計，不重算過去。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "年數合計=2+1=3，X3折舊=300000×2/3=200000元",
          "why": "新的兩年中第一年權數2。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X3末帳面=302000−200000=102000元",
          "why": "選C。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "102000元；單位：新臺幣元；選項：C",
          "why": "把變更折舊方法追溯前兩年、忽略新殘值或把年數合計當直線。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "22e743c48472915b7d524d3263a88e8069f086cc086082248ce0140999053ceb",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|19": {
      "questionId": "115-09-2-19",
      "subject": "會計學",
      "questionNumber": 19,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "銀行借款10000000元；20%原X2/6/30到期；X1/12/15已簽展延協議至X3/6/30",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "一年內到期金額=10000000×20%=2000000；若報導日前已具可推遲超過12個月清償的權利則不列流動。",
          "why": "負債流動與非流動分類要看報導日已具備的推遲清償權利與12個月時限，非單看最初借款合約。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "原一年內到期本金=10000000×20%=2000000元",
          "why": "原合約X2/6/30須還20%。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X1/12/15簽延期協議在X1/12/31報導日前",
          "why": "報導日已有有效展延安排。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "新到期日X3/6/30距X1/12/31超過12個月",
          "why": "200萬可列非流動。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "其餘8000000元均X3年底後到期",
          "why": "其餘不屬流動。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X1年底流動負債=0元，選A",
          "why": "各部分到期日均超過12個月。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "0元；單位：新臺幣元；選項：A",
          "why": "只看原X2到期額，不看報導日前已完成的有效展延。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "5c5dcab67b6d0d6dbaf56771e9726a21e3f213f2136fe3c5e7166782ec5cf4b1",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|20": {
      "questionId": "115-09-2-20",
      "subject": "會計學",
      "questionNumber": 20,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "每年付息280000元；X5年底帳面5803274元；X6年底帳面5755405元；流通六年",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "溢價攤銷=現金付息−有效利息費用；有效利率=有效利息費用/期初帳面。",
          "why": "有效利息法：利息費用=期初帳面價值×有效利率；付息=面額×票面利率；溢價攤銷=付息−利息費用。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "溢價攤銷=5803274−5755405=47869元",
          "why": "帳面減少表示溢價攤銷。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X6利息費用=280000−47869=232131元",
          "why": "現金利息扣溢價攤銷。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "有效利率≈232131/5803274≈4%",
          "why": "低於票面利率，②對。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "帳面餘額逐年降 ⇒利息費用=帳面×固定有效利率逐年降",
          "why": "①對。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "六年現金利息=280000×6=1680000元",
          "why": "現金付息合計。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "溢價使有效利息費用合計低於現金付息合計",
          "why": "③說大於錯。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "現金利息固定、利息費用逐年下降 ⇒差額(溢價攤銷)逐年增加",
          "why": "④說遞減錯；選A。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "A（①②）；單位：新臺幣元；有效利率約4%；選項：A",
          "why": "把溢價攤銷方向和有效利息費用的方向混淆。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "63ab6226b25babdeff478eefd3763a01ba1ce8c18de8210ce3423e3e7c55e389",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "會計學|21": {
      "questionId": "115-09-2-21",
      "subject": "會計學",
      "questionNumber": 21,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "X1年折舊費用高估$3,000；X2年12月1日始發現；不考慮所得稅",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "前期累計折舊高估額＝前期折舊費用多提額＝$3,000",
          "why": "判斷錯誤造成抵減資產科目及前期盈餘的高低，決定更正分錄的借貸方向。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X1折舊費用多提＝$3,000",
          "why": "題幹給定前期折舊高估金額。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X1累計折舊高估＝+$3,000",
          "why": "多計折舊費用時同步多貸累計折舊。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X1前期損益與權益低估＝$3,000",
          "why": "費用高估使以前年度盈餘偏低（題目不考所得稅）。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X2更正借：累計折舊—機器設備 $3,000",
          "why": "借記抵減資產科目可減少原本過高的累計折舊。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "X2更正貸：追溯適用及追溯重編之影響數 $3,000",
          "why": "因錯誤屬X1前期，調整以前年度權益影響，而非沖本期費用。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "借方$3,000＝貸方$3,000；對應選項C",
          "why": "更正分錄借貸平衡。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "借累計折舊$3,000／貸追溯適用及追溯重編之影響數$3,000；單位：新臺幣元；選項：C",
          "why": "把X1前期錯誤誤當X2當期折舊費用回轉，選A；或把方向顛倒選D。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "ab84aebcc2c1c7481708884de96f15e2419f9beb767f71d2549150815e48bd07",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "經濟學|30": {
      "questionId": "115-09-2-30",
      "subject": "經濟學",
      "questionNumber": 30,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "辰氏企業自行車製造商；短期成本項目與產量Q無關",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "固定是總額固定，不是每單位固定；成本需區分總成本與平均成本。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "短期TFC總固定成本不會隨產量Q增減；",
          "why": "工廠租金每個月先固定付，例如這個月多做或少做幾台車，這筆『總租金』不會因數量變；但把租金分給每一台車算，做越多台，每台分攤越少。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "TVC變動成本隨Q變，AFC=TFC/Q隨Q增加而下降，AC=TC/Q也依Q不同，故A。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "A總固定成本TFC在短期相關產量範圍內與Q無關，直接符合題目要求。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "6978feb1ffc00354f8cf35383c25f48bcdc6194949677aed3ba6904105a0a9d8",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "經濟學|31": {
      "questionId": "115-09-2-31",
      "subject": "經濟學",
      "questionNumber": 31,
      "answerCandidate": "D",
      "aiAnswer": "D",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "市場有眾多同質農產品供需者；小張是價格接受者，市場價格P固定（沒有提供實際數字）",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "TR=P×Q；AR=TR/Q",
          "why": "推導完全競爭廠商平均收益和市場價格相等。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "單位價格固定為P",
          "why": "個別小攤是價格接受者，不能自行改價。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "銷售Q單位，總收益TR=P×Q",
          "why": "每個產品都按相同市場價格賣。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "平均收益AR=TR/Q",
          "why": "用總收入除以賣出商品數量。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "AR=(P×Q)/Q=P（Q＞0）",
          "why": "約掉Q，平均每單位收益等於售價。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "因此D：完全競爭，平均收益等於價格",
          "why": "四選項只有D同時市場型態與收益敘述正確。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "AR=P；單位：每單位貨幣收入（題目未定價）；選項：D",
          "why": "把完全競爭廠商TR誤畫為倒U型；或混淆AR與MR。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "8b8d7d613f270a6a98f3fb6dbeef54f07ab0cdde68b21c5d569f014bd098c830",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "經濟學|32": {
      "questionId": "115-09-2-32",
      "subject": "經濟學",
      "questionNumber": 32,
      "answerCandidate": "B",
      "aiAnswer": "B",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "完全競爭廠商；長期與短期經營決策；比較P與AVC、AC",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "短期固定成本為沉沒或無法避免的成本；短期歇業和長期退出不是同一個決策。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論",
          "content": "完全競爭短期若價格P低於平均變動成本AVC，收益連可避免的變動成本都無法回收，短期應歇業，B。",
          "why": "賣一個東西收的錢，如果連做這個東西要用的材料工錢都不夠，越做越吃虧，短期先不要做比較好。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "B說P低於AVC時短期歇業，連做出商品的變動成本都收不回，符合停產條件。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "f21892d4f83ad55e0d74b4f5fd1b26f7a3f592ccb1972900db8df01a12f3919c",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "經濟學|33": {
      "questionId": "115-09-2-33",
      "subject": "經濟學",
      "questionNumber": 33,
      "answerCandidate": "B",
      "aiAnswer": "B",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "廠商具有獨占定價權；以利潤極大化為目標；一般邊際成本MC＞0（推導嚴格大於1的前提）",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "MR=P×(1−1/|Ed|)；MR=MC",
          "why": "說明獨占廠商在正邊際成本下為何選在需求富彈性區段。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "利潤極大：MR=MC",
          "why": "增加一件商品的收益與成本相等時是一般內部最適條件。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "若MC＞0，則MR＞0",
          "why": "最適時MR等於正的邊際成本。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "MR=P×(1−1/|Ed|)，且P＞0",
          "why": "獨占者的邊際收益與需求彈性之關係。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "1−1/|Ed|＞0 ⇒ |Ed|＞1",
          "why": "MR為正須括號為正，需求須有彈性。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "因此②『需求彈性大於1』成立（指絕對值），候選B",
          "why": "套用一般教材默認正邊際成本的獨占利潤最大化情境。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "|Ed|＞1，僅②（B）；單位：無單位（彈性係數）；選項：B",
          "why": "將獨占的需求曲線當水平線，或把虧損等同立即短期歇業。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "cb6c043034ecbf9923d72e533028d318c27e7bfa4b1715a66c14d51586ddccce",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "經濟學|34": {
      "questionId": "115-09-2-34",
      "subject": "經濟學",
      "questionNumber": 34,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": false,
      "title": "解題步驟",
      "steps": [
        {
          "title": "整理題意",
          "content": "AI伺服器市場僅兩間廠商；寡占／雙占；跟跌不跟漲；折彎需求與價格僵固",
          "why": "避免只看選項猜答案。",
          "kind": "given"
        },
        {
          "title": "確定適用觀念",
          "content": "雙占是一種寡占；廠商相依、默契與競爭策略造成需求曲線折彎，非所有寡占都一定採同策略。",
          "why": "由課程定義判斷，而非憑直覺。",
          "kind": "concept"
        },
        {
          "title": "依題目推論（1）",
          "content": "寡占廠商在折彎需求模型中可能採『跟跌不跟漲』：競爭者降價會跟進，對方漲價則不跟，因而價格僵固。",
          "why": "只有兩家大公司賣相似AI伺服器。一家降價，另一家怕客人跑掉也可能降；一家漲價，另一家可能先不漲，好讓客人來買，所以價錢不一定常常變。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（2）",
          "content": "A說可能，合理。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "依題目推論（3）",
          "content": "B『邊際收益膨脹缺口』混用術語，C說商品必定同質過度武斷，D說兩家面對相同需求彈性不符合折彎需求的彈性分段。",
          "why": "承接前一個判斷，繼續驗證題幹條件。",
          "kind": "reasoning"
        },
        {
          "title": "核對答案選項",
          "content": "A用『可能』表示兩家公司可採跟跌不跟漲，符合寡占價格僵固模型的策略相依特徵，因此正確。",
          "why": "與其餘選項的差異可對照 A-D 個別解說。",
          "kind": "answer"
        }
      ],
      "originalImageSha256": "5141e911e1925cc80d8f0f464688be2c333edb30994cce535f7c378485567b02",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "經濟學|35": {
      "questionId": "115-09-2-35",
      "subject": "經濟學",
      "questionNumber": 35,
      "answerCandidate": "A",
      "aiAnswer": "A",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "市場每單位勞動工資W＝1,500元；MRP_L表示多雇一單位勞動增加的收益",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "增雇邊際利潤＝MRP_L－W；內部最適條件MRP_L＝W",
          "why": "以增雇後多賺的收益與工資成本比較，判斷繼續雇用、減少雇用或達到最適。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "W＝1,500元",
          "why": "題幹提供每單位勞動工資。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "若MRP_L＞1,500，則MRP_L－1,500＞0",
          "why": "新增員工帶來正的邊際利潤，應多雇用。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "若MRP_L＜1,500，則MRP_L－1,500＜0",
          "why": "再雇人會使利潤下降，應少雇用。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "若MRP_L＝1,500，則MRP_L－1,500＝0",
          "why": "在一般內部最適點，增雇的邊際利益與成本相等。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "因此A：MRP_L＞1,500元時多雇用勞動",
          "why": "選項A與邊際利潤的正負一致。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "選項A（多雇用）；單位：新臺幣元／單位勞動；選項：A",
          "why": "MRP_L＞W時錯認已達利潤極大；忘記邊際利潤還是正的。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "33c6184848bcb91c79f7238f5e9d99ec4b87113742c236dfa74b78dd2554a9c4",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "經濟學|36": {
      "questionId": "115-09-2-36",
      "subject": "經濟學",
      "questionNumber": 36,
      "answerCandidate": "B",
      "aiAnswer": "B",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "甲＝對角線與洛倫茲曲線之間面積；乙＝對角線下三角形扣除甲；座標軸各自0～100%，可標準化為單位正方形",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "G＝甲/(甲＋乙)，甲＋乙＝(1×1)/2＝1/2",
          "why": "以曲線與完全平均線的夾面積占比衡量所得分配不均程度。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "甲＋乙＝1/2",
          "why": "單位正方形對角線以下是面積為1/2的三角形。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "G＝甲/(1/2)＝2甲",
          "why": "分母固定，因此G與甲面積成正比。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "甲越小⇒G越小⇒越接近完全均等線",
          "why": "曲線越貼近對角線，所得分配差異越小。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "若G=0⇒甲=0、乙=1/2",
          "why": "完全均等時沒有夾面積，剩餘三角形全部是乙。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "若G=1⇒甲=1/2、乙=0",
          "why": "極端不均時夾面積占滿下三角形。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "故選B：甲面積越小，所得分配越平均",
          "why": "與面積及G的單調關係一致。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "選B；甲越小G越小且所得越平均；單位：無單位（吉尼係數）；選項：B",
          "why": "誤把甲變小視為不平等變大，或誤說G=0時乙=0。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "91d3a9865c9bab491e3e35fef0b94712588dd83df34ab4089a2da4f0437f17ab",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    },
    "經濟學|37": {
      "questionId": "115-09-2-37",
      "subject": "經濟學",
      "questionNumber": 37,
      "answerCandidate": "C",
      "aiAnswer": "C",
      "needsReview": false,
      "reviewReason": null,
      "hasSteps": true,
      "hasExamCalculation": true,
      "title": "考題計算式｜逐步解題",
      "steps": [
        {
          "title": "整理題目已知",
          "content": "原工作每月38,000元；新自媒體每月40,000元；沒有提供其他工資／成本數據",
          "why": "核對題目原本提供的數值、單位及限制，不另外假設。",
          "kind": "given"
        },
        {
          "title": "挑選公式與用途",
          "content": "經濟租＝現職報酬－移轉賺額",
          "why": "從次佳工作推得留在新工作的最低必要報酬，再求超額部分。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "次佳用途＝原餐廳服務員",
          "why": "唯一已知可替代工作是離職前的餐廳職位。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "原餐廳報酬＝38,000元/月",
          "why": "即留在當前工作時放棄的次佳可得報酬。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "移轉賺額＝38,000元/月",
          "why": "依題目簡化假設，保有現職至少需補償前職所得。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "現職自媒體收入＝40,000元/月",
          "why": "題目提供目前得到的月收入。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "經濟租＝40,000－38,000＝2,000元/月",
          "why": "目前報酬超過最低移轉需求部分。",
          "kind": "formula"
        },
        {
          "title": "代入與運算",
          "content": "選項C：移轉賺額38,000元/月",
          "why": "不是把40,000目前收入誤稱移轉賺額。",
          "kind": "formula"
        },
        {
          "title": "計算結果及對應選項",
          "content": "移轉賺額38,000元／月；經濟租2,000元／月；選C；單位：新臺幣元／月；選項：C",
          "why": "把移轉賺額錯當目前收入40,000，或把2,000直接稱準租。",
          "kind": "result"
        }
      ],
      "originalImageSha256": "5a85327b1c306c60f53e5c3268bdb927d3438fbc0ca768e6ddf34c3553a1107b",
      "independentTeachingQA": "PENDING",
      "officialFinalVerified": false,
      "source": "現有原圖草稿與完整計算（待獨立教學複核）"
    }
  },
  "readyQuestionCount": 71
};
