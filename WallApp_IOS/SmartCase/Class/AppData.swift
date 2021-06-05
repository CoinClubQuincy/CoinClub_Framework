//
//  AppData.swift
//  AMM
//
//  Created by KMSOFT on 28/09/17.
//  Copyright © 2017 KMSOFT. All rights reserved.
//

import Foundation
import UIKit

class AppData
{
    var utility: Utility = Utility()
    var appDelegate: AppDelegate!
    var homeViewController: SerialViewController!
    
    var storyboard: UIStoryboard!
    var isPhoneUnlocked: Bool = false
    var selectedImage: UIImage?
    var selectedColor: UIColor?
    
    var senderText: String?
    var reciverText: String?
    
    static let sharedInstance: AppData = {
        let instance = AppData()
        return instance
    }()
}
