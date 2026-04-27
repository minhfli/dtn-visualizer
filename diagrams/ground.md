sequenceDiagram
    participant UAV
    participant Ground

    loop Periodic Beacon
        UAV ->> Ground: BEACON
    end

    Note over Ground: Kiểm tra hiện có đang trao đổi không
    alt Not in session
        Ground ->> UAV: GROUND_HELLO
    else Already in session
        Note over Ground: Bỏ qua BEACON
    end

    Note over UAV: Bắt đầu gửi thông điệp đến Ground

    loop While UAV has bundles for Ground
        UAV ->> Ground: BUNDLE
        Ground -->> UAV: BUNDLE_ACK
    end

    UAV ->> Ground: FERRY_HELLO

    Note over Ground: Bắt đầu gửi bundle đến UAV

    loop While Ground has bundles
        Ground ->> UAV: BUNDLE
        
        alt UAV still has buffer
            UAV -->> Ground: BUNDLE_ACK_AND_ACCEPT_TRANSFER
        else UAV buffer full
            UAV -->> Ground: BUNDLE_ACK
        end
    end

    alt Connection lost
        Note over UAV,Ground: Phiên kết thúc do mất kết nối
    else No more bundles (both sides)
        Note over UAV,Ground: Phiên kết thúc bình thường
    else UAV sends only BUNDLE_ACK
        Note over UAV,Ground: UAV không còn khả năng nhận thêm
    end