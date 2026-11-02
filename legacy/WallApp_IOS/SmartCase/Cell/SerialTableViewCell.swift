//
//  SerialTableViewCell.swift
//  SmartCase
//
//  Created by Squareroot on 13/07/18.
//  Copyright © 2018 Squareroot. All rights reserved.
//

import UIKit

class SerialTableViewCell: UITableViewCell {

    @IBOutlet weak var cardName: UIButton!
    @IBOutlet weak var cardImage: UIImageView!
    override func awakeFromNib() {
        super.awakeFromNib()
        // Initialization code
    }

    override func setSelected(_ selected: Bool, animated: Bool) {
        super.setSelected(selected, animated: animated)

        // Configure the view for the selected state
    }

}
