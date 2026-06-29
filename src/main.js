import kaboom from "kaboom";

// Kaboom 엔진 초기화
kaboom({
    width: 800,
    height: 600,
    background: [ 121, 208, 107 ], // 귀여운 잔디밭 색상
});

// 그래픽 에셋 로드 (대체 텍스트 또는 이모지로 간단하게 구성)
loadBean(); // Kaboom의 기본 캐릭터인 'bean' 사용

// 메인 게임 씬
scene("main", () => {
    // 맵 구성 (간단한 울타리와 나무 느낌)
    const map = [
        "============",
        "=          =",
        "=   @      =",
        "=          =",
        "=      @   =",
        "=          =",
        "============",
    ];

    const levelCfg = {
        width: 64,
        height: 64,
        "=": () => [
            rect(64, 64),
            color(139, 69, 19), // 나무 울타리 색상
            area(),
            solid(),
        ],
        "@": () => [
            circle(24),
            color(34, 139, 34), // 나무 색상
            area(),
            solid(),
        ],
    };

    addLevel(map, levelCfg);

    // 플레이어 추가
    const player = add([
        sprite("bean"), // 귀여운 콩 캐릭터
        pos(120, 120),
        area(),
        solid(),
        "player",
    ]);

    // 플레이어 이동 속도
    const SPEED = 200;

    // 상하좌우 이동 로직
    onKeyDown("left", () => {
        player.move(-SPEED, 0);
    });
    onKeyDown("right", () => {
        player.move(SPEED, 0);
    });
    onKeyDown("up", () => {
        player.move(0, -SPEED);
    });
    onKeyDown("down", () => {
        player.move(0, SPEED);
    });

    // 카메라가 플레이어를 따라다니게 설정
    onUpdate(() => {
        camPos(player.pos);
    });
});

// 게임 시작
go("main");
