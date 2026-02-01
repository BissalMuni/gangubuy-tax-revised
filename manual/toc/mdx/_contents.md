
content/
├── acquisition/                           # 취득세
│   ├── rates/                             # 세율
│   │   ├── realestate/                    # 부동산 (§11)
│   │   │   ├── housing/                   # 주택
│   │   │   │   ├── general-v1.0.mdx       # 유상거래 (§11①8: 1~3%)
│   │   │   │   ├── inheritance-v1.0.mdx   # 상속 (§11①1나: 2.8%)
│   │   │   │   ├── gift-v1.0.mdx          # 증여 (§11①2: 3.5%)
│   │   │   │   ├── original-v1.0.mdx      # 원시취득/신축 (§11①3: 2.8%)
│   │   │   │   ├── multi-house-v1.0.mdx   # 다주택자 중과 (§13의2①2,3)
│   │   │   │   ├── corporate-v1.0.mdx     # 법인 취득 중과 (§13의2①1)
│   │   │   │   └── luxury-v1.0.mdx        # 고급주택 중과 (§13⑤3)
│   │   │   ├── farmland/                  # 농지
│   │   │   │   ├── general-v1.0.mdx       # 유상거래 (§11①7가: 3%)
│   │   │   │   ├── inheritance-v1.0.mdx   # 상속 (§11①1가: 2.3%)
│   │   │   │   └── gift-v1.0.mdx          # 증여 (§11①2: 3.5%)
│   │   │   └── non-farmland/              # 농지 외 (건물+토지)
│   │   │       ├── general-v1.0.mdx       # 유상거래 (§11①7나: 4%)
│   │   │       ├── inheritance-v1.0.mdx   # 상속 (§11①1나: 2.8%)
│   │   │       ├── gift-v1.0.mdx          # 증여 (§11①2: 3.5%)
│   │   │       └── original-v1.0.mdx      # 원시취득 (§11①3: 2.8%, §11③)
│   │   ├── non-realestate/                # 부동산 외 (§12)
│   │   │   └── non-realestate-v1.0.mdx    # 차량/선박/기계장비/항공기/입목/회원권 통합
│   │   └── common/                        # 공통 (물건 횡단 적용)
│   │       ├── division-v1.0.mdx          # 분할취득 (§11①5,6: 2.3%)
│   │       ├── metro-surcharge-v1.0.mdx   # 과밀억제권역 중과 (§13①②)
│   │       ├── luxury-surcharge-v1.0.mdx  # 사치성재산 중과 (§13⑤: 골프/오락장/선박)
│   │       ├── special-rates-v1.0.mdx     # 세율 특례/경감 (§15)
│   │       ├── rate-application-v1.0.mdx  # 세율 적용/추징 (§16)
│   │       ├── exemption-v1.0.mdx         # 면세점 (§17: 50만원)
│   │       └── housing-count-v1.0.mdx     # 주택 수 판단 (§13의3)
│   ├── themes/                            # 테마별 통합규정
│   │   ├── multi-house-v1.0.mdx           # 다주택자 중과 (§13의2 통합)
│   │   └── first-time-buyer-v1.0.mdx      # 생애최초 주택취득 감면 (§36의3)
│   └── standard/                          # 과세표준
│       └── standard-v1.0.mdx              # 과세표준
├── property/                              # 재산세
│   └── ...
└── vehicle/                               # 자동차세
    └── ...