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
    }
  },
  "readyQuestionCount": 15
};
