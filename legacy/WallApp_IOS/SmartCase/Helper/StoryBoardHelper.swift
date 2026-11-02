//
//  StoryBoardHelper.swift
//  iLinked
//
//  Created by KMSOFT on 18/04/18.
//  Copyright © 2018 KMSOFT. All rights reserved.
//

import Foundation
import UIKit

class StoryBoardHelper {
    
    static let MAIN_STORYBOARD = UIStoryboard(name: "Main", bundle: nil)
    
    static func getSelectImageViewController() -> SelectImageViewController {
        return MAIN_STORYBOARD.instantiateViewController(withIdentifier: "SelectImageViewController") as! SelectImageViewController
    }
    
    static func getAddCardViewController() -> AddCardViewController {
        return MAIN_STORYBOARD.instantiateViewController(withIdentifier: "AddCardViewController") as! AddCardViewController
    }
}
