//
//  CardModel.swift
//  SmartCase
//
//  Created by Squareroot on 13/07/18.
//  Copyright © 2018 Squareroot. All rights reserved.
//

import Foundation
import CoreData
class CardModel {
//    var id: String?
    var cardName: String?
    var cardColor: String?
    var cardImage: Data?
    var coreObject: NSManagedObject!
    var isUpdate: Bool?
}
