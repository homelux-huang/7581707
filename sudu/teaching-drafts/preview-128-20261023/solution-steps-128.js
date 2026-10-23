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
    }
  },
  "readyQuestionCount": 8
};
